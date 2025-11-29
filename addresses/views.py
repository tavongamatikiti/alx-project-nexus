from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Address
from .serializers import AddressSerializer


class AddressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user addresses.

    Provides full CRUD operations for addresses:
    - list: GET /api/addresses/
    - create: POST /api/addresses/
    - retrieve: GET /api/addresses/{id}/
    - update: PUT /api/addresses/{id}/
    - partial_update: PATCH /api/addresses/{id}/
    - destroy: DELETE /api/addresses/{id}/

    Permissions: IsAuthenticated, users can only access their own addresses.
    """
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter addresses to only show addresses belonging to the current user.
        """
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Automatically set the user to the current authenticated user.
        """
        serializer.save(user=self.request.user)
