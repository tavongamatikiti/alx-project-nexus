from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductSerializer
from addresses.serializers import AddressSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderItem with product snapshot.
    """
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'order',
            'product',
            'product_title',
            'product_price',
            'quantity',
            'subtotal'
        ]
        read_only_fields = ['id', 'order', 'product_title', 'product_price', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order with nested items and addresses.
    """
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = AddressSerializer(read_only=True)
    billing_address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'order_id',
            'user',
            'status',
            'subtotal',
            'discount_amount',
            'total',
            'shipping_address',
            'billing_address',
            'coupon',
            'items',
            'created_at',
            'updated_at',
            'confirmed_at'
        ]
        read_only_fields = [
            'order_id',
            'user',
            'subtotal',
            'discount_amount',
            'total',
            'created_at',
            'updated_at',
            'confirmed_at'
        ]


class CreateOrderSerializer(serializers.Serializer):
    """
    Serializer for creating an order from cart.
    """
    shipping_address_id = serializers.IntegerField(required=True)
    billing_address_id = serializers.IntegerField(required=False)
    coupon_code = serializers.CharField(max_length=50, required=False, allow_blank=True)
    use_shipping_as_billing = serializers.BooleanField(default=False)
