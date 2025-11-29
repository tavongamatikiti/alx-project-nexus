from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Coupon
from .serializers import (
    CouponSerializer,
    CouponValidateSerializer,
    CouponValidateResponseSerializer
)


class CouponViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing coupons (admin-only).

    Provides full CRUD operations for coupons:
    - list: GET /api/coupons/
    - create: POST /api/coupons/
    - retrieve: GET /api/coupons/{id}/
    - update: PUT /api/coupons/{id}/
    - partial_update: PATCH /api/coupons/{id}/
    - destroy: DELETE /api/coupons/{id}/

    Permissions: IsAdminUser (staff only)
    """
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]


@extend_schema(
    request=CouponValidateSerializer,
    responses={200: CouponValidateResponseSerializer},
    description="Validate a coupon code and calculate discount amount"
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def validate_coupon(request):
    """
    Validate a coupon code.

    POST /api/coupons/validate/

    Request body:
    {
        "code": "SUMMER2024",
        "subtotal": "500.00"
    }

    Response:
    {
        "valid": true,
        "message": "Coupon is valid",
        "discount_amount": "50.00",
        "coupon": {...}
    }
    """
    serializer = CouponValidateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    code = serializer.validated_data['code']
    subtotal = serializer.validated_data['subtotal']

    try:
        coupon = Coupon.objects.get(code__iexact=code)
    except Coupon.DoesNotExist:
        return Response({
            'valid': False,
            'message': 'Coupon code not found'
        }, status=status.HTTP_404_NOT_FOUND)

    # Check if coupon is valid
    is_valid, message = coupon.is_valid()

    if not is_valid:
        return Response({
            'valid': False,
            'message': message
        }, status=status.HTTP_200_OK)

    # Check minimum purchase amount
    if subtotal < coupon.min_purchase_amount:
        return Response({
            'valid': False,
            'message': f'Minimum purchase amount is {coupon.min_purchase_amount} ETB'
        }, status=status.HTTP_200_OK)

    # Calculate discount
    discount_amount = coupon.calculate_discount(subtotal)

    return Response({
        'valid': True,
        'message': 'Coupon is valid',
        'discount_amount': str(discount_amount),
        'coupon': CouponSerializer(coupon).data
    }, status=status.HTTP_200_OK)
