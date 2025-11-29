from rest_framework.generics import ListAPIView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.conf import settings
from .models import Category
from .serializers import CategorySerializer
from drf_spectacular.utils import extend_schema, OpenApiExample


@extend_schema(
    summary="List all categories",
    description="Returns a list of all product categories available in the store. Cached for 15 minutes.",
    responses={200: CategorySerializer(many=True)},
    examples=[
        OpenApiExample(
            "Categories Example",
            value=[
                {"id": 1, "name": "Books", "slug": "books"},
                {"id": 2, "name": "Electronics", "slug": "electronics"},
            ]
        )
    ],
)
class CategoryList(ListAPIView):
    """
    List all categories with view-level caching.
    Categories are cached for 15 minutes since they don't change frequently.
    """
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    @method_decorator(cache_page(settings.CACHE_TTL))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
