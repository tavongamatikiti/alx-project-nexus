from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Order


@shared_task(bind=True, max_retries=3)
def send_order_confirmation_email(self, order_id):
    """
    Send order confirmation email to customer.
    Retries up to 3 times if fails.
    """
    try:
        order = Order.objects.select_related('user', 'shipping_address').get(order_id=order_id)

        subject = f'Order Confirmation - Order #{order.order_id}'

        # Plain text message
        message = f"""
Hello {order.user.get_full_name() or order.user.username},

Thank you for your order!

Order Details:
- Order ID: {order.order_id}
- Status: {order.get_status_display()}
- Subtotal: {order.subtotal} ETB
- Discount: {order.discount_amount} ETB
- Total: {order.total} ETB

Shipping Address:
{order.shipping_address.full_name}
{order.shipping_address.address_line1}
{order.shipping_address.city}, {order.shipping_address.state}
{order.shipping_address.country}

We will send you another email when your payment is confirmed.

Thank you for shopping with us!

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

        return f'Order confirmation email sent to {order.user.email}'

    except Order.DoesNotExist:
        return f'Order {order_id} not found'
    except Exception as exc:
        # Retry after 60 seconds
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_order_status_update_email(self, order_id, new_status):
    """
    Send email when order status is updated.
    """
    try:
        order = Order.objects.select_related('user').get(order_id=order_id)

        subject = f'Order Status Update - Order #{order.order_id}'

        status_messages = {
            'confirmed': 'Your payment has been confirmed!',
            'processing': 'Your order is being processed.',
            'shipped': 'Your order has been shipped!',
            'delivered': 'Your order has been delivered.',
            'cancelled': 'Your order has been cancelled.',
        }

        message = f"""
Hello {order.user.get_full_name() or order.user.username},

{status_messages.get(new_status, 'Your order status has been updated.')}

Order Details:
- Order ID: {order.order_id}
- New Status: {order.get_status_display()}
- Total: {order.total} ETB

Thank you for shopping with us!

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

        return f'Status update email sent to {order.user.email}'

    except Order.DoesNotExist:
        return f'Order {order_id} not found'
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
