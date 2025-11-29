import uuid
from django.db import models
from django.conf import settings
from decimal import Decimal


class Order(models.Model):
    """
    Model representing a customer order.
    Tracks order status, pricing, addresses, and applied coupons.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    order_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Pricing
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total before discount"
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Discount applied from coupon"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Final total after discount"
    )

    # Addresses (snapshot at order time)
    shipping_address = models.ForeignKey(
        'addresses.Address',
        on_delete=models.SET_NULL,
        null=True,
        related_name='shipping_orders'
    )
    billing_address = models.ForeignKey(
        'addresses.Address',
        on_delete=models.SET_NULL,
        null=True,
        related_name='billing_orders'
    )

    # Coupon
    coupon = models.ForeignKey(
        'coupons.Coupon',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when order was confirmed (payment completed)"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Order {self.order_id} - {self.user.username} ({self.status})"


class OrderItem(models.Model):
    """
    Individual item in an order.
    Stores snapshot of product details at time of order.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE
    )

    # Snapshot product details at order time
    product_title = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)

    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="quantity * product_price"
    )

    class Meta:
        indexes = [
            models.Index(fields=['order']),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.product_title} in Order {self.order.order_id}"
