from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from .models import Order, OrderItem
from .serializers import OrderSerializer, CreateOrderSerializer
from .tasks import send_order_confirmation_email, send_order_status_update_email
from cart.models import Cart
from addresses.models import Address
from coupons.models import Coupon
from products.models import Product


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_order(request):
    """
    Create order from user's cart.
    Validates addresses, applies coupon, creates order with items, clears cart.
    """
    serializer = CreateOrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = request.user
    shipping_address_id = serializer.validated_data['shipping_address_id']
    billing_address_id = serializer.validated_data.get('billing_address_id')
    coupon_code = serializer.validated_data.get('coupon_code', '').strip()
    use_shipping_as_billing = serializer.validated_data.get('use_shipping_as_billing', False)

    # Get cart
    try:
        cart = Cart.objects.prefetch_related('items__product').get(user=user)
    except Cart.DoesNotExist:
        return Response(
            {'error': 'Cart not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    if not cart.items.exists():
        return Response(
            {'error': 'Cart is empty'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate shipping address
    try:
        shipping_address = Address.objects.get(id=shipping_address_id, user=user)
    except Address.DoesNotExist:
        return Response(
            {'error': 'Invalid shipping address'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Determine billing address
    if use_shipping_as_billing:
        billing_address = shipping_address
    elif billing_address_id:
        try:
            billing_address = Address.objects.get(id=billing_address_id, user=user)
        except Address.DoesNotExist:
            return Response(
                {'error': 'Invalid billing address'},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        billing_address = shipping_address

    # Calculate subtotal
    subtotal = Decimal('0.00')
    for item in cart.items.all():
        subtotal += item.subtotal

    # Validate and apply coupon
    discount_amount = Decimal('0.00')
    coupon = None
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code)
            is_valid, message = coupon.is_valid()

            if not is_valid:
                return Response(
                    {'error': f'Invalid coupon: {message}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if subtotal < coupon.min_purchase_amount:
                return Response(
                    {'error': f'Minimum purchase amount for this coupon is {coupon.min_purchase_amount} ETB'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            discount_amount = coupon.calculate_discount(subtotal)
        except Coupon.DoesNotExist:
            return Response(
                {'error': 'Invalid coupon code'},
                status=status.HTTP_404_NOT_FOUND
            )

    total = subtotal - discount_amount

    # Create order and order items atomically
    with transaction.atomic():
        # Check stock availability with row-level locking
        for cart_item in cart.items.select_related('product'):
            product = Product.objects.select_for_update().get(id=cart_item.product.id)
            if product.stock < cart_item.quantity:
                return Response(
                    {'error': f'Insufficient stock for {product.title}. Only {product.stock} available.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Create order
        order = Order.objects.create(
            user=user,
            status='pending',
            subtotal=subtotal,
            discount_amount=discount_amount,
            total=total,
            shipping_address=shipping_address,
            billing_address=billing_address,
            coupon=coupon
        )

        # Create order items (snapshot product details)
        for cart_item in cart.items.select_related('product'):
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_title=cart_item.product.title,
                product_price=cart_item.product.price,
                quantity=cart_item.quantity,
                subtotal=cart_item.subtotal
            )

        # Increment coupon usage
        if coupon:
            coupon.used_count += 1
            coupon.save(update_fields=['used_count'])

        # Clear cart
        cart.items.all().delete()

    # Send order confirmation email asynchronously
    send_order_confirmation_email.delay(str(order.order_id))

    return Response(
        OrderSerializer(order).data,
        status=status.HTTP_201_CREATED
    )


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing and retrieving user's orders.
    Read-only - orders cannot be modified directly after creation.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            'items__product',
            'shipping_address',
            'billing_address',
            'coupon'
        )

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def update_status(self, request, pk=None):
        """
        Admin-only endpoint to update order status.
        Sets confirmed_at timestamp when status changes to 'confirmed'.
        """
        order = self.get_object()
        new_status = request.data.get('status')

        if not new_status:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status

        # Set confirmed_at timestamp when order is confirmed
        if new_status == 'confirmed' and not order.confirmed_at:
            order.confirmed_at = timezone.now()

        order.save()

        # Send status update email asynchronously
        send_order_status_update_email.delay(str(order.order_id), new_status)

        return Response(OrderSerializer(order).data)
