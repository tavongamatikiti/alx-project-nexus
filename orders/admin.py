from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_title', 'product_price', 'quantity', 'subtotal']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_id',
        'user',
        'status',
        'total',
        'created_at',
        'confirmed_at'
    ]
    list_filter = ['status', 'created_at', 'confirmed_at']
    search_fields = ['order_id', 'user__username', 'user__email']
    readonly_fields = [
        'order_id',
        'user',
        'subtotal',
        'discount_amount',
        'total',
        'created_at',
        'updated_at',
        'confirmed_at'
    ]
    fieldsets = [
        ('Order Information', {
            'fields': ['order_id', 'user', 'status']
        }),
        ('Pricing', {
            'fields': ['subtotal', 'discount_amount', 'total', 'coupon']
        }),
        ('Addresses', {
            'fields': ['shipping_address', 'billing_address']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at', 'confirmed_at']
        }),
    ]
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product_title', 'quantity', 'subtotal']
    list_filter = ['order__status']
    search_fields = ['product_title', 'order__order_id']
    readonly_fields = ['order', 'product', 'product_title', 'product_price', 'quantity', 'subtotal']
