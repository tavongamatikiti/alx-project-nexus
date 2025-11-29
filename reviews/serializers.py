from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review model with user and product information.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    product_title = serializers.CharField(source='product.title', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id',
            'user',
            'username',
            'product',
            'product_title',
            'rating',
            'comment',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5 stars")
        return value


class CreateReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a review.
    User is automatically set from request context.
    """
    class Meta:
        model = Review
        fields = ['product', 'rating', 'comment']

    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5 stars")
        return value

    def validate(self, data):
        """Check if user has already reviewed this product."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            product = data.get('product')
            if Review.objects.filter(user=request.user, product=product).exists():
                raise serializers.ValidationError(
                    "You have already reviewed this product. You can update your existing review instead."
                )
        return data
