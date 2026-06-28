from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

from .models import Order, OrderItem, Address


# ── Helpers ────────────────────────────────────────────────────────────────

def is_manager(user):
    return user.groups.filter(name="Manager").exists()


# ── Analytics view ─────────────────────────────────────────────────────────

def analytics_view(request):
    if not request.user.is_staff:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()

    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)

    total_revenue = Order.objects.aggregate(t=Sum("total_price"))["t"] or 0
    total_orders = Order.objects.count()
    total_users = User.objects.filter(is_staff=False).count()

    revenue_30d = Order.objects.filter(
        created_at__gte=thirty_days_ago
    ).aggregate(t=Sum("total_price"))["t"] or 0

    orders_by_status = (
        Order.objects.values("status")
        .annotate(count=Count("id"), revenue=Sum("total_price"))
        .order_by("-count")
    )

    top_products = (
        OrderItem.objects.values("product__name")
        .annotate(total_qty=Sum("quantity"), total_revenue=Sum(F("price") * F("quantity")))
        .order_by("-total_qty")[:10]
    )

    revenue_by_category = (
        OrderItem.objects.values("product__category__name")
        .annotate(total_qty=Sum("quantity"), total_revenue=Sum(F("price") * F("quantity")))
        .order_by("-total_revenue")
    )

    orders_per_day = (
        Order.objects.filter(created_at__gte=thirty_days_ago)
        .extra(select={"day": "DATE(created_at)"})
        .values("day")
        .annotate(count=Count("id"), revenue=Sum("total_price"))
        .order_by("-day")
    )

    context = {
        **admin.site.each_context(request),
        "title": "Analytics",
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_users": total_users,
        "revenue_30d": revenue_30d,
        "orders_by_status": orders_by_status,
        "top_products": top_products,
        "revenue_by_category": revenue_by_category,
        "orders_per_day": orders_per_day,
    }
    return render(request, "admin/analytics.html", context)


# ── Inlines ────────────────────────────────────────────────────────────────

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price")

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# ── Order Admin ────────────────────────────────────────────────────────────

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_price", "created_at")
    list_filter = ("status", "created_at", "user")
    search_fields = ("user__username", "user__email", "shipping_address")
    readonly_fields = ("created_at", "updated_at")
    inlines = [OrderItemInline]
    fieldsets = (
        ("Order Info", {"fields": ("user", "status", "total_price", "shipping_cost")}),
        ("Shipping", {"fields": ("shipping_address", "notes")}),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    ordering = ("-created_at",)
    actions = ["calculate_total_revenue", "mark_as_delivered", "mark_as_shipped"]

    def get_urls(self):
        urls = super().get_urls()
        custom = [path("analytics/", self.admin_site.admin_view(analytics_view), name="orders_analytics")]
        return custom + urls

    # ── Permissions ────────────────────────────────────────────────────────

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or is_manager(request.user)

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or is_manager(request.user)

    # ── Actions ────────────────────────────────────────────────────────────

    @admin.action(description="Calculate total revenue for selected orders")
    def calculate_total_revenue(self, request, queryset):
        total = queryset.aggregate(total=Sum("total_price"))["total"]
        self.message_user(request, f"Total revenue: ${total or 0:.2f}")

    @admin.action(description="Mark selected as Delivered")
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status="delivered")
        self.message_user(request, f"{updated} order(s) marked as Delivered.")

    @admin.action(description="Mark selected as Shipped")
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status="shipped")
        self.message_user(request, f"{updated} order(s) marked as Shipped.")


# ── Address Admin ──────────────────────────────────────────────────────────

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("full_name", "city", "user", "is_default")
    list_filter = ("is_default", "country", "city")
    search_fields = ("full_name", "user__username", "city")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Contact", {"fields": ("user", "full_name", "phone")}),
        ("Address", {"fields": ("street", "city", "state", "postal_code", "country")}),
        ("Settings", {"fields": ("is_default",)}),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    ordering = ("-is_default", "-updated_at")

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
