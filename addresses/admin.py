from django.contrib import admin
from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'address_type', 'city', 'country', 'is_default', 'created_at']
    list_filter = ['address_type', 'country', 'is_default']
    search_fields = ['full_name', 'user__username', 'city', 'postal_code']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
