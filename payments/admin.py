from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "payment_method", "status", "amount", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("order__id", "transaction_id")
    readonly_fields = ("created_at", "updated_at", "transaction_id")
    fieldsets = (
        ("Order", {"fields": ("order",)}),
        (
            "Payment",
            {"fields": ("payment_method", "amount", "status", "transaction_id")},
        ),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    ordering = ("-created_at",)
