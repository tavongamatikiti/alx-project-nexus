from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Payment


@shared_task(bind=True, max_retries=3)
def send_payment_confirmation_email(self, payment_id):
    """
    Send payment confirmation email to customer.
    Includes receipt details and order information.
    """
    try:
        payment = Payment.objects.select_related('order__user', 'order__shipping_address').get(payment_id=payment_id)
        order = payment.order

        subject = f'Payment Confirmation - Order #{order.order_id}'

        message = f"""
Hello {order.user.get_full_name() or order.user.username},

Your payment has been successfully processed!

Payment Details:
- Payment ID: {payment.payment_id}
- Transaction ID: {payment.transaction_id}
- Amount Paid: {payment.amount} {payment.currency}
- Payment Method: {payment.payment_method or 'N/A'}
- Payment Date: {payment.payment_date.strftime('%B %d, %Y at %I:%M %p') if payment.payment_date else 'N/A'}

Order Details:
- Order ID: {order.order_id}
- Status: {order.get_status_display()}
- Total: {order.total} ETB

Your order is now confirmed and will be processed shortly.

Shipping Address:
{order.shipping_address.full_name}
{order.shipping_address.address_line1}
{order.shipping_address.city}, {order.shipping_address.state}
{order.shipping_address.country}

Thank you for your purchase!

Best regards,
ALX Ecommerce Team
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            fail_silently=False,
        )

        return f'Payment confirmation email sent to {order.user.email}'

    except Payment.DoesNotExist:
        return f'Payment {payment_id} not found'
    except Exception as exc:
        # Retry after 60 seconds
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_payment_failed_email(self, payment_id):
    """
    Send email notification when payment fails.
    """
    try:
        payment = Payment.objects.select_related('order__user').get(payment_id=payment_id)
        order = payment.order

        subject = f'Payment Failed - Order #{order.order_id}'

        message = f"""
Hello {order.user.get_full_name() or order.user.username},

Unfortunately, your payment could not be processed.

Payment Details:
- Payment ID: {payment.payment_id}
- Transaction ID: {payment.transaction_id}
- Amount: {payment.amount} {payment.currency}
- Status: {payment.get_payment_status_display()}

Order Details:
- Order ID: {order.order_id}
- Total: {order.total} ETB

Please try again or contact our support team if the problem persists.

Best regards,
ALX Ecommerce Team
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            fail_silently=False,
        )

        return f'Payment failure email sent to {order.user.email}'

    except Payment.DoesNotExist:
        return f'Payment {payment_id} not found'
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
