from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, initiate_payment, verify_payment

router = DefaultRouter()
router.register(r'', PaymentViewSet, basename='payment')

urlpatterns = [
    path('initiate/', initiate_payment, name='initiate-payment'),
    path('verify/', verify_payment, name='verify-payment'),
    path('', include(router.urls)),
]
