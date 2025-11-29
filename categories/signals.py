from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Category


@receiver([post_save, post_delete], sender=Category)
def clear_category_cache(sender, instance, **kwargs):
    """
    Clear category list cache when a category is created, updated, or deleted.
    This ensures the cached category list stays fresh.
    """
    # Clear all category-related caches
    cache.delete_pattern("ecommerce:*categories*")

    # Also clear product caches since products reference categories
    cache.delete_pattern("ecommerce:products_list_*")