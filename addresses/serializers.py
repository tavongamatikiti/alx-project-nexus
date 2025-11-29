from rest_framework import serializers
from .models import Address


class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer for Address model.
    """
    class Meta:
        model = Address
        fields = [
            'id',
            'user',
            'address_type',
            'full_name',
            'phone_number',
            'address_line1',
            'address_line2',
            'city',
            'state',
            'postal_code',
            'country',
            'is_default',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validate address data.
        """
        # User is automatically set from request.user in the view
        return data
