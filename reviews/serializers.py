from rest_framework import serializers
from .models import Review


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["rating", "comment"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        validated_data["product_id"] = self.context["product_id"]
        return super().create(validated_data)


class ReviewDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "user_name",
            "rating",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user_name", "created_at", "updated_at"]
