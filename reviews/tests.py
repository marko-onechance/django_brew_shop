"""Tests for reviews app."""
import pytest
from decimal import Decimal
from django.contrib.auth.models import User

from products.models import Category, Product
from reviews.models import Review


@pytest.fixture
def category(db):
    return Category.objects.create(name="Lagers", slug="lagers")


@pytest.fixture
def product(db, category):
    return Product.objects.create(
        name="Pilsner",
        slug="pilsner",
        description="A classic pilsner",
        price=Decimal("4.50"),
        stock=20,
        category=category,
    )


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="reviewer",
        email="reviewer@example.com",
        password="pass1234",
    )


@pytest.mark.django_db
class TestReviewModel:
    def test_review_creation(self, user, product):
        review = Review.objects.create(
            product=product,
            user=user,
            rating=4,
            comment="Great beer!",
        )
        assert review.rating == 4
        assert review.comment == "Great beer!"

    def test_review_str(self, user, product):
        review = Review.objects.create(
            product=product,
            user=user,
            rating=5,
            comment="Excellent!",
        )
        assert "reviewer" in str(review)
        assert "Pilsner" in str(review)
        assert "5" in str(review)

    def test_unique_review_per_user_product(self, user, product):
        """A user can only leave one review per product."""
        Review.objects.create(product=product, user=user, rating=3, comment="OK")
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            Review.objects.create(product=product, user=user, rating=4, comment="Good")

    def test_product_average_rating(self, product):
        """Test average rating calculation on the product."""
        user1 = User.objects.create_user(username="u1", password="pass")
        user2 = User.objects.create_user(username="u2", password="pass")
        Review.objects.create(product=product, user=user1, rating=4, comment="Good")
        Review.objects.create(product=product, user=user2, rating=2, comment="OK")
        avg = product.get_average_rating()
        assert avg == pytest.approx(3.0)

    def test_product_review_count(self, product, user):
        Review.objects.create(product=product, user=user, rating=5, comment="Excellent!")
        count = product.get_review_count()
        assert count == 1
