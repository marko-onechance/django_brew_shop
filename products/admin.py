from django.contrib import admin
from django.db.models import Count
from .models import Category, Product


def is_manager(user):
    return user.groups.filter(name="Manager").exists()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    list_filter = ("created_at", "parent")
    ordering = ("name",)

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or is_manager(request.user)

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or is_manager(request.user)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "is_active", "created_at", "get_orders_count")
    list_filter = ("is_active", "category", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        ("Main Info", {"fields": ("name", "slug", "description")}),
        ("Category & Price", {"fields": ("category", "price")}),
        ("Stock", {"fields": ("stock", "is_active")}),
        ("Image", {"fields": ("image",)}),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    actions = ["activate_products", "deactivate_products"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(orders_count=Count("orderitem"))

    def get_orders_count(self, obj):
        return obj.orders_count
    get_orders_count.short_description = "Orders"
    get_orders_count.admin_order_field = "orders_count"

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

    @admin.action(description="Activate selected products")
    def activate_products(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} product(s) activated.")

    @admin.action(description="Deactivate selected products")
    def deactivate_products(self, request, queryset):
        if not request.user.is_superuser:
            self.message_user(request, "Only superusers can deactivate products.", level="error")
            return
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} product(s) deactivated.")
