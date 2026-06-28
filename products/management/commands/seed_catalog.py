from decimal import Decimal
from typing import Any

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from products.models import Category, Product

CATEGORY_TREE: list[tuple[str, str | None]] = [
    ("Ingredients", None),
    ("Kits", None),
    ("Hops", "Ingredients"),
    ("Malts", "Ingredients"),
    ("Yeast", "Ingredients"),
]

PRODUCTS: list[tuple[str, str, str, int, str, str]] = [
    ("Cascade Hops", "Hops", "4.50", 100, "cascade_hops.jpg",
     "Classic American hop with citrus and floral notes. Great for pale ales and IPAs."),
    ("Centennial Hops", "Hops", "5.00", 80, "centennial_hops.jpg",
     "Medium-intensity hop with floral and citrus character. A versatile American hop."),
    ("Citra Hops", "Hops", "6.50", 60, "citra_hops.jpg",
     "Intense tropical and citrus aroma. One of the most popular hops for modern IPAs."),
    ("Mosaic Hops", "Hops", "6.75", 50, "mosaic_hops.jpg",
     "Complex berry, tropical fruit, and herbal notes. A brewer's favorite for NEIPAs."),
    ("Saaz Hops", "Hops", "5.25", 70, "saaz_hops.jpg",
     "The classic noble hop from Czech Republic. Earthy, spicy, and herbal."),
    ("Maris Otter Malt", "Malts", "2.20", 200, "maris_otter_malt.jpg",
     "Premium English base malt with a rich, biscuity flavor. Ideal for ales."),
    ("Pilsner Malt", "Malts", "2.00", 200, "pilsner_malt.jpg",
     "Light, clean base malt for lagers and pilsners. Low color, high fermentability."),
    ("Caramel Malt", "Malts", "2.50", 150, "caramel_malt.jpg",
     "Adds sweetness, color, and body. Essential for amber ales and stouts."),
    ("Unmalted Wheat", "Malts", "1.90", 180, "unmalted_wheat.jpg",
     "Adds haze, body, and a soft mouthfeel. Perfect for wheat beers and NEIPAs."),
    ("Safale US-05 Yeast", "Yeast", "3.80", 120, "safale_us05_yeast.jpg",
     "America's most popular dry ale yeast. Clean, neutral profile and high attenuation."),
    ("Imperial Yeast", "Yeast", "8.00", 40, "imperial_yeast.jpg",
     "Premium liquid yeast with high cell count. Exceptional performance and flavor."),
    ("West Coast IPA Kit", "Kits", "39.99", 25, "ipa_kit.jpg",
     "Complete all-grain kit for a classic West Coast IPA. Includes hops, malt, and yeast."),
]


class Command(BaseCommand):
    """Populate the database with demo categories and products (idempotent)."""

    help = "Create demo categories and products with images (idempotent)."

    def handle(self, *args: Any, **options: Any) -> None:
        cats: dict[str, Category] = {}
        for name, parent_name in CATEGORY_TREE:
            parent = cats[parent_name] if parent_name else None
            cats[name], created = Category.objects.get_or_create(
                name=name, defaults={"parent": parent}
            )
            if created:
                self.stdout.write(f"  Created category: {name}")

        img_dir = settings.BASE_DIR / "static" / "img" / "products"

        for name, cat_name, price, stock, image, description in PRODUCTS:
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    "category": cats[cat_name],
                    "price": Decimal(price),
                    "stock": stock,
                    "description": description,
                },
            )
            if created:
                self.stdout.write(f"  Created product: {name}")

            src = img_dir / image
            media_missing = not product.image or not product.image.storage.exists(product.image.name)
            if src.exists() and media_missing:
                with src.open("rb") as fh:
                    product.image.save(image, File(fh), save=True)
                self.stdout.write(f"  Attached image: {image}")

        self.stdout.write(self.style.SUCCESS("Catalog populated successfully."))
