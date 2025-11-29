from rest_framework import serializers
from .models import Product
from categories.serializers import CategorySerializer


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Product._meta.get_field("category").remote_field.model.objects.all(),
        write_only=True,
        source="category"
    )

    class Meta:
        model = Product
        fields = [
            "id", "title", "slug", "description", "price",
            "category", "category_id", "stock",
            "is_active", "created_at", "updated_at"
        ]
        read_only_fields = ["slug", "created_at", "updated_at"]
