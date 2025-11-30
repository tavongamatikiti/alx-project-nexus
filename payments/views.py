import os
import uuid
import requests
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Payment
from .serializers import PaymentSerializer, InitiatePaymentSerializer
from .tasks import send_payment_confirmation_email, send_payment_failed_email
from orders.models import Order
from products.models import Product


CHAPA_SECRET_KEY = os.getenv('CHAPA_SECRET_KEY')
CHAPA_BASE_URL = os.getenv('CHAPA_BASE_URL', 'https://api.chapa.co/v1')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def initiate_payment(request):
    """
    Initiate payment with Chapa for an order.
    Creates Payment record and returns Chapa checkout URL.
    """
    serializer = InitiatePaymentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    order_id = serializer.validated_data['order_id']
    return_url = serializer.validated_data.get('return_url', 'http://localhost:3000/payment/success')

    # Validate order belongs to user
    try:
        order = Order.objects.select_related('user').get(order_id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response(
            {'error': 'Order not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check order is pending payment
    if order.status != 'pending':
        return Response(
            {'error': f'Order is already {order.status}. Cannot initiate payment.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Generate unique transaction ID
    transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"

    # Create payment record
    payment = Payment.objects.create(
        order=order,
        transaction_id=transaction_id,
        amount=order.total,
        currency='ETB',
        payment_status='pending'
    )

    # Prepare Chapa API request
    chapa_data = {
        'amount': str(order.total),
        'currency': 'ETB',
        'email': request.user.email,
        'first_name': request.user.first_name or request.user.username,
        'last_name': request.user.last_name or '',
        'tx_ref': transaction_id,
        'callback_url': os.getenv('CHAPA_CALLBACK_URL', f"{request.scheme}://{request.get_host()}/api/payments/verify/"),
        'return_url': return_url,
        'customization': {
            'title': 'Order Payment',
            'description': f'Order {str(order.order_id)[:8]}'
        }
    }

    headers = {
        'Authorization': f'Bearer {CHAPA_SECRET_KEY}',
        'Content-Type': 'application/json'
    }

    try:
        # Call Chapa API to initialize payment
        response = requests.post(
            f'{CHAPA_BASE_URL}/transaction/initialize',
            json=chapa_data,
            headers=headers,
            timeout=10
        )

        # Check response before raising
        if response.status_code != 200:
            error_detail = response.text
            payment.payment_status = 'failed'
            payment.save(update_fields=['payment_status'])
            return Response(
                {'error': f'Chapa API error: {error_detail}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        chapa_response = response.json()

        if chapa_response.get('status') == 'success':
            checkout_url = chapa_response['data']['checkout_url']

            # Update payment with Chapa reference and checkout URL
            payment.chapa_reference = transaction_id
            payment.checkout_url = checkout_url
            payment.save(update_fields=['chapa_reference', 'checkout_url'])

            return Response({
                'payment_id': payment.payment_id,
                'checkout_url': checkout_url,
                'transaction_id': transaction_id
            }, status=status.HTTP_201_CREATED)
        else:
            payment.payment_status = 'failed'
            payment.save(update_fields=['payment_status'])
            return Response(
                {'error': 'Failed to initialize payment with Chapa'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except requests.RequestException as e:
        payment.payment_status = 'failed'
        payment.save(update_fields=['payment_status'])
        return Response(
            {'error': f'Payment gateway error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'POST'])
def verify_payment(request):
    """
    Verify payment with Chapa after user completes payment.
    Updates payment status, order status, and deducts inventory stock.

    Chapa sends: GET /api/payments/verify/?tx_ref=<transaction_id>
    """
    # Get transaction reference from query params (Chapa sends 'tx_ref' or 'trx_ref')
    tx_ref = request.GET.get('tx_ref') or request.GET.get('trx_ref')

    if not tx_ref:
        return Response(
            {'error': 'tx_ref parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        payment = Payment.objects.select_related('order').get(transaction_id=tx_ref)
    except Payment.DoesNotExist:
        return Response(
            {'error': 'Payment not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # If payment already completed, return success
    if payment.payment_status == 'completed':
        return Response({
            'status': 'success',
            'message': 'Payment already verified',
            'payment': PaymentSerializer(payment).data
        })

    # Verify with Chapa API
    headers = {
        'Authorization': f'Bearer {CHAPA_SECRET_KEY}'
    }

    try:
        response = requests.get(
            f'{CHAPA_BASE_URL}/transaction/verify/{payment.transaction_id}',
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        chapa_response = response.json()

        if chapa_response.get('status') == 'success':
            chapa_data = chapa_response['data']

            # Check if payment was successful on Chapa side
            if chapa_data.get('status') == 'success':
                # Update payment and order atomically with stock deduction
                with transaction.atomic():
                    # Update payment status
                    payment.payment_status = 'completed'
                    payment.payment_method = chapa_data.get('method', 'unknown')
                    payment.payment_date = timezone.now()
                    payment.save(update_fields=['payment_status', 'payment_method', 'payment_date'])

                    # Update order status
                    order = payment.order
                    order.status = 'confirmed'
                    order.confirmed_at = timezone.now()
                    order.save(update_fields=['status', 'confirmed_at'])

                    # Deduct stock for each order item
                    for order_item in order.items.select_related('product'):
                        product = Product.objects.select_for_update().get(id=order_item.product.id)

                        # Validate stock availability
                        if product.stock < order_item.quantity:
                            raise ValueError(
                                f'Insufficient stock for {product.title}. Only {product.stock} available.'
                            )

                        # Deduct stock
                        product.stock -= order_item.quantity
                        product.save(update_fields=['stock'])

                # Send payment confirmation email asynchronously
                send_payment_confirmation_email.delay(str(payment.payment_id))

                return Response({
                    'status': 'success',
                    'message': 'Payment verified and order confirmed',
                    'payment': PaymentSerializer(payment).data
                })
            else:
                # Payment failed on Chapa side
                payment.payment_status = 'failed'
                payment.save(update_fields=['payment_status'])

                # Send payment failure email asynchronously
                send_payment_failed_email.delay(str(payment.payment_id))

                return Response({
                    'status': 'failed',
                    'message': 'Payment verification failed',
                    'payment': PaymentSerializer(payment).data
                }, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(
                {'error': 'Failed to verify payment with Chapa'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except ValueError as e:
        # Stock validation error - refund would be needed here in production
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except requests.RequestException as e:
        return Response(
            {'error': f'Payment verification error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing payment history.
    Read-only - payments cannot be modified directly.
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user).select_related('order')
