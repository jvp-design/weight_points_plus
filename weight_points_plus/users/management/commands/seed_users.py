from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Delete and re-create any non-superusers"

    def handle(self, *args, **options):
        new_users = [
            dict(username="user", email="user@example.com", password="string"),
            dict(username="user1", email="user1@example.com", password="string1"),
            dict(username="user2", email="user2@example.com", password="string2"),
            dict(username="user3", email="user3@example.com", password="string3"),
            dict(username="user4", email="user4@example.com", password="string4"),
            dict(username="user5", email="user5@example.com", password="string5"),
        ]
        User.objects.filter(is_superuser=False).delete()
        for user in new_users:
            User.objects.create_user(**user)

        self.stdout.write(self.style.SUCCESS("Successfully created new users"))
