from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings as django_settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from products.models import Product
from .cart import Cart
from .models import Order, OrderItem
from . import analytics


@require_POST
def cart_add(request, slug):
    cart = Cart(request)
    product = get_object_or_404(Product, slug=slug)
    quantity = int(request.POST.get("quantity", 1))

    if quantity > product.stock:
        messages.error(
            request, f"Cannot add more than {product.stock} items of {product.name}."
        )
    else:
        cart.add(product=product, quantity=quantity)
        messages.success(request, f"Added {product.name} to cart.")

    return redirect("cart_detail")


@require_POST
def cart_remove(request, slug):
    cart = Cart(request)
    product = get_object_or_404(Product, slug=slug)
    cart.remove(product)
    messages.info(request, f"Removed {product.name} from cart.")
    return redirect("cart_detail")


@require_POST
def cart_update(request, slug):
    cart = Cart(request)
    product = get_object_or_404(Product, slug=slug)
    quantity = int(request.POST.get("quantity", 1))

    if quantity > product.stock:
        messages.error(
            request,
            f"Cannot update to more than {product.stock} items of {product.name}.",
        )
    else:
        cart.add(product=product, quantity=quantity, override_quantity=True)
        messages.success(request, f"Updated {product.name} quantity to {quantity}.")

    return redirect("cart_detail")


def cart_detail(request):
    cart = Cart(request)
    return render(request, "orders/cart_detail.html", {"cart": cart})


@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, "Your cart is empty.")
        return redirect("product_list")

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        city = request.POST.get("city", "")
        address = request.POST.get("address")
        payment_method = request.POST.get("payment_method", "cod")

        if not all([full_name, phone, address]):
            messages.error(request, "Please fill in all the required fields.")
            return render(request, "orders/checkout.html", {"cart": cart})

        shipping_text = f"{full_name}\n{phone}\n{city}\n{address}"

        order = Order.objects.create(
            user=request.user,
            total_price=cart.get_total_price(),
            shipping_address=shipping_text,
        )

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                price=item["price"],
                quantity=item["quantity"],
            )
            product = item["product"]
            product.stock -= item["quantity"]
            product.save()

        cart.clear()

        try:
            if request.user.email:
                send_mail(
                    subject=f"Order #{order.id} Confirmed – Hop & Barley",
                    message=(
                        f"Thank you, {request.user.username}!\n\n"
                        f"Your order #{order.id} has been placed.\n"
                        f"Total: ${order.total_price}\n"
                        f"Shipping to: {order.shipping_address}\n\n"
                        f"We will notify you when it ships."
                    ),
                    from_email=django_settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=True,
                )
            send_mail(
                subject=f"New Order #{order.id} – Hop & Barley",
                message=(
                    f"New order received!\n\n"
                    f"User: {request.user.username} ({request.user.email})\n"
                    f"Order #{order.id}\n"
                    f"Total: ${order.total_price}\n"
                    f"Payment: {payment_method}\n"
                    f"Shipping to: {order.shipping_address}"
                ),
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[django_settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request, f"Your order #{order.id} has been placed successfully!")
        return redirect("account")

    return render(request, "orders/checkout.html", {"cart": cart})


@user_passes_test(lambda u: u.is_staff, login_url="/users/login/")
def analytics_dashboard(request):
    top = list(analytics.top_products(limit=5))
    max_qty = top[0]["total_qty"] if top else 1

    status_colors = {
        "pending": {"color": "#d4900a", "label": "Pending"},
        "paid": {"color": "#4a9e52", "label": "Paid"},
        "shipped": {"color": "#3a7fc1", "label": "Shipped"},
        "delivered": {"color": "#2e7d32", "label": "Delivered"},
        "cancelled": {"color": "#e05252", "label": "Cancelled"},
    }
    by_status = analytics.orders_by_status()
    total_orders_for_bar = max(by_status.values()) if by_status else 1
    statuses = [
        {
            "key": key,
            "label": status_colors.get(key, {}).get("label", key.title()),
            "color": status_colors.get(key, {}).get("color", "#888"),
            "count": count,
            "pct": round(count / total_orders_for_bar * 100),
        }
        for key, count in by_status.items()
    ]

    top_seller = top[0] if top else None

    return render(request, "orders/analytics.html", {
        "revenue": analytics.total_revenue(),
        "order_count": analytics.order_count(),
        "top_seller": top_seller,
        "statuses": statuses,
        "top_products": top,
        "max_qty": max_qty,
    })
