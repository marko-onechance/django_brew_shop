import pytest
from django.urls import reverse
from products.models import Category, Product


@pytest.mark.django_db
class TestCatalog:
    def test_category_creation(self):
        cat = Category.objects.create(name="Test Category", slug="test-category")
        assert cat.name == "Test Category"
        assert str(cat) == "Test Category"

    def test_product_creation(self):
        cat = Category.objects.create(name="Test Category", slug="test-category")
        prod = Product.objects.create(
            category=cat, name="Test Product", slug="test-product", price=10.0, stock=5
        )
        assert prod.name == "Test Product"
        assert prod.price == 10.0

    def test_product_list_view(self, client):
        url = reverse("product_list")
        response = client.get(url)
        assert response.status_code == 200

    def test_product_detail_view(self, client):
        cat = Category.objects.create(name="Test Category", slug="test-category")
        prod = Product.objects.create(
            category=cat, name="Test Product", slug="test-product", price=10.0, stock=5
        )
        url = reverse("product_detail", args=[prod.slug])
        response = client.get(url)
        assert response.status_code == 200
        assert b"Test Product" in response.content
