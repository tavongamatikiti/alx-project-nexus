"""
URL configuration for ecommerce project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from products.views import ProductViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.http import HttpResponse


def home_view(request):
    content = """
    <h1>ALX Ecommerce Project NEXUS</h1>
    <p>E-commerce Backend API</p>

    <h2>Available API Endpoints</h2>

    <h3>Products</h3>
    <ul>
        <li><a href="/api/products/">GET /api/products/</a> - List products</li>
        <li>/api/products/&lt;id&gt;/ - Retrieve, update, delete product</li>
        <li>Filtering: /api/products/?category__id=1</li>
        <li>Search: /api/products/?search=laptop</li>
        <li>Ordering: /api/products/?ordering=price</li>
    </ul>

    <h3>Categories</h3>
    <ul>
        <li><a href="/api/categories/">GET /api/categories/</a> - List categories</li>
    </ul>

    <h3>Authentication</h3>
    <ul>
        <li>/api/auth/register/ - Register new user</li>
        <li>/api/auth/login/ - Login (get JWT tokens)</li>
        <li>/api/auth/token/refresh/ - Refresh access token</li>
    </ul>

    <h3>Admin</h3>
    <ul>
        <li><a href="/admin/">/admin/</a></li>
    </ul>

    <h3>API Documentation</h3>
    <ul>
        <li><a href="/api/schema/">/api/schema/</a> - OpenAPI schema</li>
        <li><a href="/api/docs/">/api/docs/</a> - Swagger UI</li>
        <li><a href="/api/redoc/">/api/redoc/</a> - ReDoc documentation</li>
    </ul>

    <hr>
    <p>Backend Engineering - Project Nexus (ALX)</p>
    """
    return HttpResponse(content)


router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path("api/auth/", include("users.urls")),
    path("api/categories/", include("categories.urls")),
    path("api/addresses/", include("addresses.urls")),
    path("api/coupons/", include("coupons.urls")),
    path("api/cart/", include("cart.urls")),
    path("api/", include(router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
