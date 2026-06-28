from django.urls import path
from . import views

urlpatterns = [
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<slug:slug>/", views.cart_add, name="cart_add"),
    path("cart/remove/<slug:slug>/", views.cart_remove, name="cart_remove"),
    path("cart/update/<slug:slug>/", views.cart_update, name="cart_update"),
    path("checkout/", views.checkout, name="checkout"),
    path("analytics/", views.analytics_dashboard, name="analytics"),
]
