from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, create_order

router = DefaultRouter()
router.register(r'', OrderViewSet, basename='order')

urlpatterns = [
    path('create/', create_order, name='create-order'),
    path('', include(router.urls)),
]
