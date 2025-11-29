from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_cart(request):
    """
    Get the current user's cart with all items.

    GET /api/cart/
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_to_cart(request):
    """
    Add a product to cart or update quantity if already exists.

    POST /api/cart/add/
    Body: {"product_id": 1, "quantity": 2}
    """
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)

    if not product_id:
        return Response(
            {'error': 'product_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return Response(
            {'error': 'Product not found or inactive'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check stock availability
    if product.stock < quantity:
        return Response(
            {'error': f'Only {product.stock} items available in stock'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get or create cart
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Check if product already in cart
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not item_created:
        # Update quantity if item already exists
        new_quantity = cart_item.quantity + quantity
        if product.stock < new_quantity:
            return Response(
                {'error': f'Only {product.stock} items available in stock'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart_item.quantity = new_quantity
        cart_item.save()

    serializer = CartSerializer(cart)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_cart_item(request, item_id):
    """
    Update quantity of a cart item.

    PATCH /api/cart/item/{item_id}/
    Body: {"quantity": 3}
    """
    try:
        cart_item = CartItem.objects.get(
            id=item_id,
            cart__user=request.user
        )
    except CartItem.DoesNotExist:
        return Response(
            {'error': 'Cart item not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    quantity = request.data.get('quantity')
    if quantity is None:
        return Response(
            {'error': 'quantity is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if quantity <= 0:
        # Delete item if quantity is 0 or negative
        cart_item.delete()
        cart = Cart.objects.get(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    # Check stock availability
    if cart_item.product.stock < quantity:
        return Response(
            {'error': f'Only {cart_item.product.stock} items available in stock'},
            status=status.HTTP_400_BAD_REQUEST
        )

    cart_item.quantity = quantity
    cart_item.save()

    cart = Cart.objects.get(user=request.user)
    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_from_cart(request, item_id):
    """
    Remove an item from cart.

    DELETE /api/cart/item/{item_id}/
    """
    try:
        cart_item = CartItem.objects.get(
            id=item_id,
            cart__user=request.user
        )
        cart_item.delete()

        cart = Cart.objects.get(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    except CartItem.DoesNotExist:
        return Response(
            {'error': 'Cart item not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def clear_cart(request):
    """
    Clear all items from cart.

    DELETE /api/cart/clear/
    """
    try:
        cart = Cart.objects.get(user=request.user)
        cart.items.all().delete()
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    except Cart.DoesNotExist:
        return Response(
            {'error': 'Cart not found'},
            status=status.HTTP_404_NOT_FOUND
        )
