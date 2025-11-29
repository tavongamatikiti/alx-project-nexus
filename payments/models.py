import uuid
from django.db import models


class Payment(models.Model):
    """
    Model representing a payment transaction via Chapa.
    Tracks payment status from initiation through completion.
    """
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    payment_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='payments'
    )

    # Transaction identifiers
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        help_text="Our internal transaction reference"
    )
    chapa_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Chapa's transaction reference (tx_ref)"
    )
    checkout_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Chapa checkout URL for customer payment"
    )

    # Payment details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Payment amount in ETB"
    )
    currency = models.CharField(
        max_length=3,
        default='ETB',
        help_text="Currency code (ETB for Ethiopian Birr)"
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Payment method used (e.g., telebirr, cbebirr)"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when payment was completed"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['transaction_id']),
        ]

    def __str__(self):
        return f"Payment {self.payment_id} for Order {self.order.order_id} - {self.payment_status}"
