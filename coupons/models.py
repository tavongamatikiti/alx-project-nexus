from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Coupon(models.Model):
    """
    Model representing a discount coupon code.
    Supports percentage and fixed amount discounts.
    """
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique coupon code (e.g., SUMMER2024)"
    )
    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        help_text="Type of discount: percentage or fixed amount"
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Discount value (e.g., 20 for 20% or 100 for 100 ETB)"
    )
    min_purchase_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Minimum purchase amount required to use this coupon"
    )
    max_uses = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of times this coupon can be used (null = unlimited)"
    )
    used_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this coupon has been used"
    )
    valid_from = models.DateTimeField(
        help_text="Date and time when coupon becomes valid"
    )
    valid_to = models.DateTimeField(
        help_text="Date and time when coupon expires"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this coupon is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code', 'is_active']),
        ]

    def __str__(self):
        if self.discount_type == 'percentage':
            return f"{self.code} - {self.discount_value}% off"
        else:
            return f"{self.code} - {self.discount_value} ETB off"

    def is_valid(self):
        """
        Check if the coupon is currently valid.
        """
        now = timezone.now()

        # Check if active
        if not self.is_active:
            return False, "Coupon is not active"

        # Check date validity
        if now < self.valid_from:
            return False, "Coupon is not yet valid"

        if now > self.valid_to:
            return False, "Coupon has expired"

        # Check usage limit
        if self.max_uses is not None and self.used_count >= self.max_uses:
            return False, "Coupon usage limit reached"

        return True, "Coupon is valid"

    def calculate_discount(self, subtotal):
        """
        Calculate discount amount based on subtotal.
        Returns the discount amount in ETB.
        """
        if self.discount_type == 'percentage':
            discount = (subtotal * self.discount_value) / 100
        else:
            discount = self.discount_value

        # Discount cannot exceed subtotal
        return min(discount, subtotal)

    def increment_usage(self):
        """
        Increment the used_count when coupon is applied to an order.
        """
        self.used_count += 1
        self.save(update_fields=['used_count'])
