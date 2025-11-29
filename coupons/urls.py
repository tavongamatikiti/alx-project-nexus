from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CouponViewSet, validate_coupon

router = DefaultRouter()
router.register(r'', CouponViewSet, basename='coupon')

urlpatterns = [
    path('validate/', validate_coupon, name='coupon-validate'),
    path('', include(router.urls)),
]
