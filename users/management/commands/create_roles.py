from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = "Create Manager group with limited permissions"

    def handle(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name="Manager")

        app_model_perms = [
            ("orders", "order", ["view", "change"]),
            ("orders", "address", ["view"]),
            ("products", "product", ["view", "change"]),
            ("products", "category", ["view", "change"]),
            ("reviews", "review", ["view"]),
            ("users", "userprofile", []),
        ]

        group.permissions.clear()
        for app_label, model_name, actions in app_model_perms:
            try:
                ct = ContentType.objects.get(app_label=app_label, model=model_name)
                for action in actions:
                    perm = Permission.objects.get(content_type=ct, codename=f"{action}_{model_name}")
                    group.permissions.add(perm)
            except (ContentType.DoesNotExist, Permission.DoesNotExist):
                pass

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} 'Manager' group successfully."))
        self.stdout.write("Permissions: view/change orders, view/change products & categories, view reviews.")
        self.stdout.write("To assign: python manage.py shell → user.groups.add(Group.objects.get(name='Manager')); user.is_staff=True; user.save()")
