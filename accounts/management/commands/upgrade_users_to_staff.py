"""
Management command to upgrade all existing users to staff role.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()  # noqa: F841


class Command(BaseCommand):
    """Upgrade all existing users to staff role."""

    help = 'Upgrade all existing users to staff role'

    def handle(self, *args, **options):
        """Handle the command execution."""
        # Get all users
        users = User.objects.all()
        updated_count = 0

        for user in users:
            if not user.is_staff:
                user.is_staff = True
                user.save()
                updated_count += 1
                self.stdout.write(f'✓ Upgraded {user.username} to staff role')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully upgraded {updated_count} users to staff role!'
            )
        )
        self.stdout.write(
            f'Total staff users now: {User.objects.filter(is_staff=True).count()}'
        )
