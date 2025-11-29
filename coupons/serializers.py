from rest_framework import serializers
from .models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    """
    Serializer for Coupon model (admin-only CRUD).
    """
    class Meta:
        model = Coupon
        fields = [
            'id',
            'code',
            'discount_type',
            'discount_value',
            'min_purchase_amount',
            'max_uses',
            'used_count',
            'valid_from',
            'valid_to',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'used_count', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validate coupon data.
        """
        # Ensure valid_from is before valid_to
        if 'valid_from' in data and 'valid_to' in data:
            if data['valid_from'] >= data['valid_to']:
                raise serializers.ValidationError(
                    "valid_from must be before valid_to"
                )

        # Ensure discount_value is appropriate for discount_type
        if 'discount_type' in data and 'discount_value' in data:
            if data['discount_type'] == 'percentage' and data['discount_value'] > 100:
                raise serializers.ValidationError(
                    "Percentage discount cannot exceed 100%"
                )

        return data


class CouponValidateSerializer(serializers.Serializer):
    """
    Serializer for validating a coupon code.
    """
    code = serializers.CharField(max_length=50)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)


class CouponValidateResponseSerializer(serializers.Serializer):
    """
    Response serializer for coupon validation.
    """
    valid = serializers.BooleanField()
    message = serializers.CharField()
    discount_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )
    coupon = CouponSerializer(required=False)
