from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from orders.models import OrderItem
from .models import Review


@login_required
def add_review(request, slug):
    if request.method == "POST":
        product = get_object_or_404(Product, slug=slug)
        rating = int(request.POST.get("rating", 5))
        comment = request.POST.get("comment", "").strip()

        has_delivered = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__status="delivered",
        ).exists()

        if not has_delivered:
            messages.error(request, "You can only review products you have received.")
            return redirect("product_detail", slug=slug)

        if Review.objects.filter(product=product, user=request.user).exists():
            messages.error(request, "You have already reviewed this product.")
            return redirect("product_detail", slug=slug)

        if comment:
            Review.objects.create(
                product=product, user=request.user, rating=rating, comment=comment
            )
            messages.success(request, "Thank you for your review!")

    return redirect("product_detail", slug=slug)
