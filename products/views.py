from decimal import Decimal, InvalidOperation
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count
from .models import Product, Category


class ProductListView(ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "object_list"
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related("category")

        # Search
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
            )

        # Filter by category (filter out empty strings from "All products" radio)
        categories = [c for c in self.request.GET.getlist("category") if c]
        if categories:
            queryset = queryset.filter(category__slug__in=categories)

        # Price range filter
        price_min = self.request.GET.get("price_min")
        price_max = self.request.GET.get("price_max")
        if price_min:
            try:
                queryset = queryset.filter(price__gte=Decimal(price_min))
            except (InvalidOperation, ValueError):
                pass
        if price_max:
            try:
                queryset = queryset.filter(price__lte=Decimal(price_max))
            except (InvalidOperation, ValueError):
                pass

        # Sorting
        sort = self.request.GET.get("sort", "-created_at")
        if sort == "popularity":
            queryset = queryset.annotate(order_count=Count("orderitem")).order_by("-order_count")
        elif sort in ["price", "-price", "-created_at"]:
            queryset = queryset.order_by(sort)
        else:
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["selected_categories"] = [c for c in self.request.GET.getlist("category") if c]
        context["price_min"] = self.request.GET.get("price_min", "")
        context["price_max"] = self.request.GET.get("price_max", "")
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return Product.objects.filter(is_active=True).prefetch_related("reviews__user")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            from orders.models import OrderItem
            context["can_review"] = OrderItem.objects.filter(
                order__user=user,
                product=self.object,
                order__status="delivered",
            ).exists()
            context["already_reviewed"] = self.object.reviews.filter(user=user).exists()
        else:
            context["can_review"] = False
            context["already_reviewed"] = False
        return context
