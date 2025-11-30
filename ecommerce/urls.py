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
    <!DOCTYPE html>
    <html>
    <head>
        <title>ALX Ecommerce Project NEXUS</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            h1 { color: #2c3e50; }
            h2 { color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; margin-top: 30px; }
            h3 { color: #7f8c8d; margin-top: 20px; }
            ul { list-style-type: none; padding: 0; }
            li { margin: 5px 0; padding: 5px; }
            a { color: #3498db; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .method { font-weight: bold; display: inline-block; width: 80px; }
            .get { color: #27ae60; }
            .post { color: #e67e22; }
            .put { color: #9b59b6; }
            .delete { color: #e74c3c; }
            .info { background: #ecf0f1; padding: 10px; border-left: 4px solid #3498db; margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>ALX Ecommerce Project NEXUS</h1>
        <p><strong>Full-Featured E-commerce Backend API with Chapa Payment Integration</strong></p>

        <div class="info">
            <strong>Base URL:</strong> http://localhost:8000<br>
            <strong>Authentication:</strong> JWT Bearer Token
        </div>

        <h2>API Endpoints</h2>

        <h3>Authentication</h3>
        <ul>
            <li><span class="method post">POST</span> /api/auth/register/ - Register new user</li>
            <li><span class="method post">POST</span> /api/auth/login/ - Login and get JWT tokens</li>
            <li><span class="method post">POST</span> /api/auth/token/refresh/ - Refresh access token</li>
        </ul>

        <h3>Products</h3>
        <ul>
            <li><span class="method get">GET</span> <a href="/api/products/">/api/products/</a> - List all products</li>
            <li><span class="method get">GET</span> /api/products/&lt;id&gt;/ - Retrieve single product</li>
            <li><span class="method post">POST</span> /api/products/ - Create product (Admin only)</li>
            <li><span class="method put">PUT</span> /api/products/&lt;id&gt;/ - Update product (Admin only)</li>
            <li><span class="method delete">DELETE</span> /api/products/&lt;id&gt;/ - Delete product (Admin only)</li>
            <li>Query params: ?category__id=1, ?search=laptop, ?ordering=price</li>
        </ul>

        <h3>Categories</h3>
        <ul>
            <li><span class="method get">GET</span> <a href="/api/categories/">/api/categories/</a> - List all categories</li>
            <li><span class="method get">GET</span> /api/categories/&lt;id&gt;/ - Retrieve single category</li>
            <li><span class="method post">POST</span> /api/categories/ - Create category (Admin only)</li>
            <li><span class="method put">PUT</span> /api/categories/&lt;id&gt;/ - Update category (Admin only)</li>
            <li><span class="method delete">DELETE</span> /api/categories/&lt;id&gt;/ - Delete category (Admin only)</li>
        </ul>

        <h3>Addresses</h3>
        <ul>
            <li><span class="method get">GET</span> /api/addresses/ - List user addresses</li>
            <li><span class="method get">GET</span> /api/addresses/&lt;id&gt;/ - Retrieve single address</li>
            <li><span class="method post">POST</span> /api/addresses/ - Create new address</li>
            <li><span class="method put">PUT</span> /api/addresses/&lt;id&gt;/ - Update address</li>
            <li><span class="method delete">DELETE</span> /api/addresses/&lt;id&gt;/ - Delete address</li>
            <li><span class="method post">POST</span> /api/addresses/&lt;id&gt;/set-default/ - Set as default address</li>
        </ul>

        <h3>Shopping Cart</h3>
        <ul>
            <li><span class="method get">GET</span> /api/cart/ - View cart items</li>
            <li><span class="method post">POST</span> /api/cart/add/ - Add item to cart</li>
            <li><span class="method put">PUT</span> /api/cart/update/&lt;id&gt;/ - Update cart item quantity</li>
            <li><span class="method delete">DELETE</span> /api/cart/remove/&lt;id&gt;/ - Remove item from cart</li>
            <li><span class="method delete">DELETE</span> /api/cart/clear/ - Clear entire cart</li>
        </ul>

        <h3>Coupons</h3>
        <ul>
            <li><span class="method get">GET</span> /api/coupons/ - List all active coupons</li>
            <li><span class="method get">GET</span> /api/coupons/&lt;id&gt;/ - Retrieve single coupon</li>
            <li><span class="method post">POST</span> /api/coupons/ - Create coupon (Admin only)</li>
            <li><span class="method post">POST</span> /api/coupons/validate/ - Validate coupon code</li>
            <li><span class="method put">PUT</span> /api/coupons/&lt;id&gt;/ - Update coupon (Admin only)</li>
            <li><span class="method delete">DELETE</span> /api/coupons/&lt;id&gt;/ - Delete coupon (Admin only)</li>
        </ul>

        <h3>Orders</h3>
        <ul>
            <li><span class="method get">GET</span> /api/orders/ - List user orders</li>
            <li><span class="method get">GET</span> /api/orders/&lt;order_id&gt;/ - Retrieve order details</li>
            <li><span class="method post">POST</span> /api/orders/create/ - Create order from cart</li>
            <li><span class="method post">POST</span> /api/orders/&lt;order_id&gt;/cancel/ - Cancel order</li>
            <li><span class="method post">POST</span> /api/orders/&lt;order_id&gt;/update-status/ - Update order status (Admin only)</li>
        </ul>

        <h3>Payments (Chapa Integration)</h3>
        <ul>
            <li><span class="method get">GET</span> /api/payments/ - List user payments</li>
            <li><span class="method get">GET</span> /api/payments/&lt;id&gt;/ - Retrieve payment details</li>
            <li><span class="method post">POST</span> /api/payments/initiate/ - Initiate Chapa payment</li>
            <li><span class="method get">GET</span> /api/payments/verify/?tx_ref=&lt;ref&gt; - Verify payment (Webhook)</li>
        </ul>

        <h3>Reviews</h3>
        <ul>
            <li><span class="method get">GET</span> /api/reviews/ - List all reviews</li>
            <li><span class="method get">GET</span> /api/reviews/&lt;id&gt;/ - Retrieve single review</li>
            <li><span class="method get">GET</span> /api/reviews/?product=&lt;id&gt; - Filter reviews by product</li>
            <li><span class="method post">POST</span> /api/reviews/ - Create product review</li>
            <li><span class="method put">PUT</span> /api/reviews/&lt;id&gt;/ - Update review</li>
            <li><span class="method delete">DELETE</span> /api/reviews/&lt;id&gt;/ - Delete review</li>
        </ul>

        <h2>API Documentation</h2>
        <ul>
            <li><a href="/api/schema/">/api/schema/</a> - OpenAPI 3.0 Schema (JSON)</li>
            <li><a href="/api/docs/">/api/docs/</a> - Interactive Swagger UI</li>
            <li><a href="/api/redoc/">/api/redoc/</a> - ReDoc Documentation</li>
        </ul>

        <h2>Admin Panel</h2>
        <ul>
            <li><a href="/admin/">/admin/</a> - Django Admin Interface</li>
        </ul>

        <hr>
        <p><strong>Backend Engineering - Project Nexus (ALX)</strong></p>
        <p><em>Django 5.2.8 | DRF 3.16.1 | PostgreSQL | Redis | Celery | Chapa Payments</em></p>
    </body>
    </html>
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
    path("api/orders/", include("orders.urls")),
    path("api/payments/", include("payments.urls")),
    path("api/reviews/", include("reviews.urls")),
    path("api/", include(router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
