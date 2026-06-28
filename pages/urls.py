from django.urls import path
from . import views

urlpatterns = [
    path("guides/", views.guides_view, name="guides"),
    path("community/", views.community_view, name="community"),
]
