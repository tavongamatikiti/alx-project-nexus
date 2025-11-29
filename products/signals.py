from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Product


@receiver([post_save, post_delete], sender=Product)
def clear_product_cache(sender, instance, **kwargs):
    """
    Clear product list cache when a product is created, updated, or deleted.
    This ensures the cached product lists stay fresh.
    """
    # Clear all product-related caches
    cache.delete_pattern("ecommerce:products_list_*")