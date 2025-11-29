from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Product
from .serializers import ProductSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample


@extend_schema_view(
    list=extend_schema(
        summary="List all active products",
        description=(
            "Returns a paginated list of active products with intelligent caching. "
            "Supports filtering by category, searching by title/description, "
            "and ordering by price or creation date. Results are cached based on query parameters."
        ),
        responses={200: ProductSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Product List Example",
                value={
                    "count": 1,
                    "results": [
                        {
                            "id": 1,
                            "title": "Book ABC",
                            "slug": "book-abc",
                            "description": "A thriller novel",
                            "price": "9.99",
                            "category": {"id": 1, "name": "Books", "slug": "books"},
                            "stock": 10,
                            "is_active": True,
                            "created_at": "2025-01-01T12:00:00Z"
                        }
                    ]
                }
            )
        ],
    ),
    create=extend_schema(
        summary="Create a new product",
        description="Creates a product with category id. The slug is generated automatically.",
        request=ProductSerializer,
        responses={201: ProductSerializer},
        examples=[
            OpenApiExample(
                "Create Product Example",
                value={
                    "title": "Laptop Lenovo",
                    "description": "High performance laptop",
                    "price": "799.99",
                    "category_id": 2,
                    "stock": 5,
                    "is_active": True
                }
            )
        ],
    ),
)
class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for products with intelligent query caching.

    Caching Strategy:
    - List views are cached based on query parameters (filters, search, ordering, page)
    - Cache keys include all query parameters to ensure unique caching
    - Cache timeout: 5 minutes (configurable in settings)
    - Cache is automatically invalidated when products are created/updated/deleted
    """
    queryset = Product.objects.filter(is_active=True).select_related("category")
    serializer_class = ProductSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]

    filterset_fields = ["category__id", "category__slug"]
    search_fields = ["title", "description"]
    ordering_fields = ["price", "created_at"]

    def list(self, request, *args, **kwargs):
        """
        List products with query-level caching.
        Cache key is generated from query parameters to ensure unique results.
        """
        # Generate cache key from query parameters
        query_params = request.query_params.urlencode()
        cache_key = f"products_list_{query_params}" if query_params else "products_list_default"

        # Try to get from cache
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            return cached_response

        # If not in cache, get from database
        response = super().list(request, *args, **kwargs)

        # Cache the response for 5 minutes
        cache.set(cache_key, response, timeout=300)

        return response

    def perform_create(self, serializer):
        """Clear product list cache when a new product is created."""
        super().perform_create(serializer)
        self._clear_product_cache()

    def perform_update(self, serializer):
        """Clear product list cache when a product is updated."""
        super().perform_update(serializer)
        self._clear_product_cache()

    def perform_destroy(self, instance):
        """Clear product list cache when a product is deleted."""
        super().perform_destroy(instance)
        self._clear_product_cache()

    def _clear_product_cache(self):
        """Clear all product-related caches."""
        # Clear all product list caches (this is a simple implementation)
        # In production, consider using cache versioning or tagged caching
        cache.delete_pattern("ecommerce:products_list_*")
