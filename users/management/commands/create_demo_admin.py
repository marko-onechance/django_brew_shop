import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Create a demo superuser for the live demo site (idempotent)."

    def handle(self, *args, **options):
        username = os.getenv("DEMO_ADMIN_USER", "admin")
        password = os.getenv("DEMO_ADMIN_PASSWORD", "admin1234")
        email = os.getenv("DEMO_ADMIN_EMAIL", "admin@hopandbarley.demo")

        if User.objects.filter(username=username).exists():
            self.stdout.write(f"  Demo admin '{username}' already exists — skipping.")
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(
            f"  Created demo superuser: {username} / {password}"
        ))
