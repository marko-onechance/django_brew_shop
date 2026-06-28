from decimal import Decimal
from django.db.models import Sum, Count

from .models import Order, OrderItem

REVENUE_STATUSES = ("paid", "shipped", "delivered")


def total_revenue():
    result = Order.objects.filter(status__in=REVENUE_STATUSES).aggregate(
        total=Sum("total_price")
    )
    return result["total"] or Decimal("0")


def order_count():
    return Order.objects.count()


def orders_by_status():
    rows = (
        Order.objects.values("status")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    return {row["status"]: row["count"] for row in rows}


def top_products(limit=5):
    return (
        OrderItem.objects.values("product__id", "product__name")
        .annotate(total_qty=Sum("quantity"))
        .order_by("-total_qty")[:limit]
    )
