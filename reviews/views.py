from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Review
from .serializers import ReviewSerializer, CreateReviewSerializer


class IsReviewOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a review to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the review
        return obj.user == request.user


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for creating, retrieving, updating, and deleting product reviews.
    - Anyone can view reviews
    - Only authenticated users can create reviews
    - Only review owner can update/delete their review
    """
    queryset = Review.objects.select_related('user', 'product')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsReviewOwnerOrReadOnly]
    filterset_fields = ['product', 'rating']
    search_fields = ['comment']
    ordering_fields = ['rating', 'created_at']

    def get_serializer_class(self):
        """Use CreateReviewSerializer for create action."""
        if self.action == 'create':
            return CreateReviewSerializer
        return ReviewSerializer

    def perform_create(self, serializer):
        """Automatically set the user to the current logged-in user."""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Only allow owner to update their review."""
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You can only update your own reviews")
        serializer.save()

    def perform_destroy(self, instance):
        """Only allow owner to delete their review."""
        if instance.user != self.request.user:
            raise PermissionDenied("You can only delete your own reviews")
        instance.delete()
