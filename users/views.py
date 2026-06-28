from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("product_list")
    else:
        form = UserCreationForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("product_list")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.info(request, "You have successfully logged out.")
    return redirect("product_list")


@login_required
def account_view(request):
    status_filter = request.GET.get("status", "")
    orders = request.user.orders.all()
    if status_filter:
        orders = orders.filter(status=status_filter)
    from orders.models import Order
    order_statuses = Order.STATUS_CHOICES
    return render(request, "users/account.html", {
        "orders": orders,
        "status_filter": status_filter,
        "order_statuses": order_statuses,
    })


@login_required
def profile_edit_view(request):
    """Edit user profile information."""
    profile = request.user.profile
    if request.method == "POST":
        bio = request.POST.get("bio", "")
        phone = request.POST.get("phone", "")
        email = request.POST.get("email", "")
        first_name = request.POST.get("first_name", "")
        last_name = request.POST.get("last_name", "")

        profile.bio = bio
        profile.phone = phone
        profile.save()

        user = request.user
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("account")
    return render(request, "users/profile_edit.html", {"profile": profile})


@login_required
def password_change_view(request):
    """Change user password."""
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect("account")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "users/password_change.html", {"form": form})
