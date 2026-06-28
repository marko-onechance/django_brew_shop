"""Tests for the REST API endpoints."""
import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from products.models import Category, Product
from orders.models import Order, OrderItem


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def category(db):
    return Category.objects.create(name="IPAs", slug="ipas")


@pytest.fixture
def product(db, category):
    return Product.objects.create(
        name="West Coast IPA",
        slug="west-coast-ipa",
        description="Hoppy West Coast IPA",
        price=Decimal("6.50"),
        stock=15,
        category=category,
    )


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="apiuser",
        email="apiuser@example.com",
        password="apipassword123",
    )


@pytest.fixture
def auth_client(db, user):
    """APIClient with valid JWT token."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def order(db, user, product):
    order = Order.objects.create(
        user=user,
        status="pending",
        total_price=Decimal("13.00"),
        shipping_address="вул. Франка 5, Львів",
    )
    OrderItem.objects.create(order=order, product=product, quantity=2, price=product.price)
    return order


# ---------------------------------------------------------------------------
# Product API Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestProductAPI:
    def test_product_list_unauthenticated(self, api_client, product):
        """Product list is publicly accessible."""
        url = "/api/products/"
        response = api_client.get(url)
        assert response.status_code == 200

    def test_product_list_returns_data(self, api_client, product):
        """Product list returns products."""
        url = "/api/products/"
        response = api_client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert data["count"] >= 1

    def test_product_detail(self, api_client, product):
        """Product detail endpoint works."""
        url = f"/api/products/{product.id}/"
        response = api_client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "West Coast IPA"

    def test_product_detail_404(self, api_client):
        """Non-existent product returns 404."""
        url = "/api/products/99999/"
        response = api_client.get(url)
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Order API Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestOrderAPI:
    def test_order_list_requires_auth(self, api_client):
        """Order list requires authentication."""
        url = "/api/orders/"
        response = api_client.get(url)
        assert response.status_code == 401

    def test_order_list_authenticated(self, auth_client, order):
        """Authenticated user can see their orders."""
        url = "/api/orders/"
        response = auth_client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1

    def test_user_sees_only_own_orders(self, auth_client, db, product):
        """User only sees their own orders, not others'."""
        other_user = User.objects.create_user(username="other", password="pass")
        Order.objects.create(
            user=other_user,
            total_price=Decimal("5.00"),
            shipping_address="Test address",
        )
        url = "/api/orders/"
        response = auth_client.get(url)
        data = response.json()
        # The authenticated user has no orders, so count should be 0
        assert data["count"] == 0


# ---------------------------------------------------------------------------
# User Registration API Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestUserRegisterAPI:
    def test_register_valid(self, api_client, db):
        url = "/api/users/register/"
        payload = {
            "username": "newregister",
            "email": "newreg@example.com",
            "password": "TestPass!234",
        }
        response = api_client.post(url, payload, format="json")
        assert response.status_code == 201
        assert User.objects.filter(username="newregister").exists()

    def test_register_missing_fields(self, api_client, db):
        url = "/api/users/register/"
        response = api_client.post(url, {}, format="json")
        assert response.status_code == 400

    def test_register_duplicate_username(self, api_client, user):
        url = "/api/users/register/"
        payload = {
            "username": "apiuser",  # already exists
            "email": "another@example.com",
            "password": "TestPass!234",
        }
        response = api_client.post(url, payload, format="json")
        assert response.status_code == 400


# ---------------------------------------------------------------------------
# JWT Auth API Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestJWTAuth:
    def test_obtain_token(self, api_client, user):
        url = "/api/users/login/"
        payload = {"username": "apiuser", "password": "apipassword123"}
        response = api_client.post(url, payload, format="json")
        assert response.status_code == 200
        data = response.json()
        assert "access" in data
        assert "refresh" in data

    def test_invalid_credentials(self, api_client, db):
        url = "/api/users/login/"
        payload = {"username": "nobody", "password": "wrongpass"}
        response = api_client.post(url, payload, format="json")
        assert response.status_code == 401

    def test_refresh_token(self, api_client, user):
        refresh = RefreshToken.for_user(user)
        url = "/api/users/token/refresh/"
        response = api_client.post(url, {"refresh": str(refresh)}, format="json")
        assert response.status_code == 200
        assert "access" in response.json()


# ---------------------------------------------------------------------------
# Swagger/Docs Accessibility Test
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestSwagger:
    def test_schema_endpoint(self, api_client):
        response = api_client.get("/api/schema/")
        assert response.status_code == 200

    def test_swagger_ui(self, api_client):
        response = api_client.get("/api/docs/")
        assert response.status_code == 200
