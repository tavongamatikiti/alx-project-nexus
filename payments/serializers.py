from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for Payment model with order reference.
    """
    order_id = serializers.UUIDField(source='order.order_id', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'payment_id',
            'order',
            'order_id',
            'transaction_id',
            'chapa_reference',
            'checkout_url',
            'amount',
            'currency',
            'payment_status',
            'payment_method',
            'created_at',
            'updated_at',
            'payment_date'
        ]
        read_only_fields = [
            'payment_id',
            'transaction_id',
            'chapa_reference',
            'checkout_url',
            'payment_status',
            'payment_method',
            'created_at',
            'updated_at',
            'payment_date'
        ]


class InitiatePaymentSerializer(serializers.Serializer):
    """
    Serializer for initiating payment for an order.
    """
    order_id = serializers.UUIDField(required=True)
    return_url = serializers.URLField(
        required=False,
        help_text="URL to redirect user after payment (optional)"
    )
