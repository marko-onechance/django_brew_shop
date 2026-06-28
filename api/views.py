from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from products.models import Product
from orders.models import Order, OrderItem
from orders.cart import Cart
from .serializers import (
    UserSerializer,
    ProductSerializer,
    OrderSerializer,
    ReviewSerializer,
)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only product list and detail, with reviews nested action."""

    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at"]

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="reviews",
        permission_classes=[permissions.IsAuthenticatedOrReadOnly],
    )
    def reviews(self, request, pk=None):
        """List or create reviews for a product."""
        product = self.get_object()

        if request.method == "GET":
            reviews_qs = product.reviews.all().select_related("user")
            serializer = ReviewSerializer(reviews_qs, many=True)
            return Response(serializer.data)

        # POST
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            has_purchased = OrderItem.objects.filter(
                order__user=request.user, product=product
            ).exists()
            if not has_purchased:
                return Response(
                    {"detail": "You must purchase this product to review it."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer.save(user=request.user, product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderViewSet(viewsets.ModelViewSet):
    """CRUD for the authenticated user's orders."""

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserRegisterView(APIView):
    """Register a new user account."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartAPIView(APIView):
    """Manage the session-based shopping cart via API."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Return current cart contents."""
        cart = Cart(request)
        items = []
        for item in cart:
            items.append({
                "product_id": item["product"].id,
                "product_name": item["product"].name,
                "quantity": item["quantity"],
                "price": str(item["price"]),
                "total_price": str(item["total_price"]),
            })
        return Response({
            "items": items,
            "total": str(cart.get_total_price()),
            "count": len(cart),
        })

    def post(self, request):
        """Add a product to the cart."""
        cart = Cart(request)
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        if quantity > product.stock:
            return Response(
                {"detail": f"Only {product.stock} items in stock."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cart.add(product=product, quantity=quantity)
        return Response({"detail": "Added to cart."}, status=status.HTTP_201_CREATED)

    def patch(self, request):
        """Update the quantity of a product in the cart."""
        cart = Cart(request)
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        if quantity > product.stock:
            return Response(
                {"detail": f"Only {product.stock} items in stock."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cart.add(product=product, quantity=quantity, override_quantity=True)
        return Response({"detail": "Cart updated."})

    def delete(self, request):
        """Remove a product from the cart, or clear the whole cart."""
        cart = Cart(request)
        product_id = request.data.get("product_id")
        if not product_id:
            cart.clear()
            return Response({"detail": "Cart cleared."})
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        cart.remove(product)
        return Response({"detail": "Item removed from cart."})
