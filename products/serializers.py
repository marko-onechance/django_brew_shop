from rest_framework import serializers
from .models import Category, Product
from reviews.models import Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description"]


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "user_name", "rating", "comment", "created_at"]
        read_only_fields = ["user_name", "created_at"]


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "price",
            "category_name",
            "image",
            "stock",
            "average_rating",
            "review_count",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_average_rating(self, obj) -> float:
        return obj.get_average_rating()

    def get_review_count(self, obj) -> int:
        return obj.get_review_count()


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "price",
            "category",
            "image",
            "stock",
            "is_active",
            "created_at",
            "reviews",
            "average_rating",
            "review_count",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_average_rating(self, obj) -> float:
        return obj.get_average_rating()

    def get_review_count(self, obj) -> int:
        return obj.get_review_count()
