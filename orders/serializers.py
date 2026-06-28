from rest_framework import serializers
from .models import Order, OrderItem, Address
from products.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Product.objects.all(), source="product"
    )

    class Meta:
        model = OrderItem
        fields = ["id", "product_id", "product_name", "quantity", "price"]
        read_only_fields = ["price"]


class OrderListSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source="items.all", many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "status_display",
            "total_price",
            "created_at",
            "items",
        ]
        read_only_fields = ["id", "created_at"]


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source="items.all", many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    items_total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "status_display",
            "total_price",
            "items_total",
            "shipping_address",
            "shipping_cost",
            "notes",
            "created_at",
            "updated_at",
            "items",
        ]
        read_only_fields = ["id", "total_price", "created_at", "updated_at"]

    def get_items_total(self, obj) -> float:
        return obj.get_items_total()


class OrderCreateSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(max_length=500)
    shipping_cost = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = serializers.CharField(required=False, allow_blank=True)
    items = OrderItemSerializer(many=True, write_only=True)

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        order = Order.objects.create(
            user=self.context["request"].user, **validated_data
        )
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "full_name",
            "phone",
            "street",
            "city",
            "state",
            "postal_code",
            "country",
            "is_default",
        ]
