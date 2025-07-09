from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Create a superuser for admin access"

    def handle(self, *args, **options):
        username = "admin"
        email = "admin@innovote.com"
        password = "admin123"

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f"Superuser '{username}' already exists!")
            )
        else:
            User.objects.create_superuser(username, email, password)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Superuser created successfully!\n"
                    f"Username: {username}\n"
                    f"Password: {password}\n"
                    f"Email: {email}\n"
                    f"\nYou can now access the admin dashboard at: /dashboard/"
                )
            )
