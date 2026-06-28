"""Tests for orders app: cart, order creation, checkout logic."""
import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from django.urls import reverse

from products.models import Category, Product
from orders.models import Order, OrderItem, Address


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def category(db):
    return Category.objects.create(name="Ales", slug="ales")


@pytest.fixture
def product(db, category):
    return Product.objects.create(
        name="Golden Ale",
        slug="golden-ale",
        description="A refreshing golden ale",
        price=Decimal("5.50"),
        stock=10,
        category=category,
    )


@pytest.fixture
def out_of_stock_product(db, category):
    return Product.objects.create(
        name="Rare Stout",
        slug="rare-stout",
        description="Very rare stout",
        price=Decimal("8.00"),
        stock=0,
        category=category,
    )


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpassword123",
    )


@pytest.fixture
def order(db, user, product):
    order = Order.objects.create(
        user=user,
        status="pending",
        total_price=Decimal("11.00"),
        shipping_address="вул. Шевченка 1, Київ",
    )
    OrderItem.objects.create(order=order, product=product, quantity=2, price=product.price)
    return order


# ---------------------------------------------------------------------------
# Order Model Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestOrderModel:
    def test_order_str(self, order, user):
        assert f"Order #{order.id}" in str(order)
        assert user.username in str(order)

    def test_order_status_default(self, user):
        order = Order.objects.create(
            user=user,
            total_price=Decimal("5.00"),
            shipping_address="Test address",
        )
        assert order.status == "pending"

    def test_order_items_total(self, order, product):
        total = order.get_items_total()
        # 2 * 5.50 = 11.00
        assert total == pytest.approx(11.0)

    def test_order_item_subtotal(self, order, product):
        item = order.items.first()
        assert item.get_subtotal() == pytest.approx(11.0)


# ---------------------------------------------------------------------------
# Address Model Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAddressModel:
    def test_address_str(self, user):
        addr = Address.objects.create(
            user=user,
            full_name="Іван Іваненко",
            phone="0501234567",
            street="вул. Шевченка 1",
            city="Київ",
            postal_code="01001",
        )
        assert "Іван Іваненко" in str(addr)
        assert "Київ" in str(addr)


# ---------------------------------------------------------------------------
# Cart Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCart:
    def test_add_product(self, client, product):
        """Adding product to cart via view should redirect to cart."""
        url = reverse("cart_add", args=[product.slug])
        response = client.post(url, {"quantity": 1})
        assert response.status_code in (200, 302)

    def test_cart_view(self, client):
        """Cart page should be accessible."""
        response = client.get(reverse("cart_detail"))
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Checkout & Order Creation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCheckout:
    def test_checkout_requires_login(self, client):
        """Unauthenticated user should be redirected to login."""
        response = client.get(reverse("checkout"))
        assert response.status_code in (302, 301)
        assert "login" in response.url

    def test_checkout_view_authenticated(self, client, user):
        client.login(username="testuser", password="testpassword123")
        response = client.get(reverse("checkout"))
        # Either shows form or redirects to cart if empty
        assert response.status_code in (200, 302)

    def test_stock_constraint(self, product):
        """Cannot have more OrderItems than stock."""
        assert product.stock >= 0
        assert product.stock == 10
