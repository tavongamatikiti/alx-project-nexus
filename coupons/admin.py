from django.contrib import admin
from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'discount_type',
        'discount_value',
        'min_purchase_amount',
        'used_count',
        'max_uses',
        'is_active',
        'valid_from',
        'valid_to'
    ]
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_to']
    search_fields = ['code']
    readonly_fields = ['used_count', 'created_at', 'updated_at']
    ordering = ['-created_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'discount_type', 'discount_value')
        }),
        ('Usage Limits', {
            'fields': ('min_purchase_amount', 'max_uses', 'used_count')
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_to', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
