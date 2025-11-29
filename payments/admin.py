from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'payment_id',
        'order',
        'transaction_id',
        'amount',
        'currency',
        'payment_status',
        'payment_method',
        'created_at',
        'payment_date'
    ]
    list_filter = ['payment_status', 'currency', 'payment_method', 'created_at']
    search_fields = ['payment_id', 'transaction_id', 'chapa_reference', 'order__order_id']
    readonly_fields = [
        'payment_id',
        'order',
        'transaction_id',
        'chapa_reference',
        'checkout_url',
        'amount',
        'currency',
        'payment_method',
        'created_at',
        'updated_at',
        'payment_date'
    ]
    fieldsets = [
        ('Payment Information', {
            'fields': ['payment_id', 'order', 'payment_status']
        }),
        ('Transaction Details', {
            'fields': ['transaction_id', 'chapa_reference', 'checkout_url']
        }),
        ('Amount', {
            'fields': ['amount', 'currency', 'payment_method']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at', 'payment_date']
        }),
    ]

    def has_add_permission(self, request):
        # Payments should only be created through the API
        return False

    def has_delete_permission(self, request, obj=None):
        # Payments should not be deleted
        return False
