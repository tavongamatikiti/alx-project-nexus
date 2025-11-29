from rest_framework import generics, permissions
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


@extend_schema(
    summary="Register a new user",
    description="Creates a new user account. Password is securely hashed.",
    request=RegisterSerializer,
    responses={201: RegisterSerializer, 400: {"detail": "Validation errors"}},
    examples=[
        OpenApiExample(
            "User Registration Example",
            value={"username": "john_doe", "email": "john@example.com", "password": "password123"}
        )
    ],
)
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(
    summary="Authenticate user",
    description="Returns access & refresh tokens for authenticated users.",
    request=CustomTokenObtainPairSerializer,
    responses={200: CustomTokenObtainPairSerializer},
    examples=[
        OpenApiExample("Login Example", value={"username": "john_doe", "password": "password123"})
    ],
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(
    summary="Refresh access token",
    description="Returns a new access token using a valid refresh token.",
)
class CustomTokenRefreshView(TokenRefreshView):
    pass
