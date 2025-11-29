from django.db import models
from django.conf import settings
from decimal import Decimal


class Cart(models.Model):
    """
    Shopping cart model with one-to-one relationship with User.
    Each authenticated user has exactly one cart.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    @property
    def total_items(self):
        """Total number of items in cart."""
        return self.items.count()

    @property
    def subtotal(self):
        """Calculate total price of all items in cart."""
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    """
    Individual item in a shopping cart.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['cart', 'product']
        indexes = [
            models.Index(fields=['cart']),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.product.title} in {self.cart.user.username}'s cart"

    @property
    def subtotal(self):
        """Calculate subtotal for this cart item."""
        return Decimal(str(self.product.price)) * self.quantity
