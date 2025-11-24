"""
Django Management Command: Create Admin User

This command creates a default administrator account for testing and initial setup.

Usage:
    python manage.py create_admin_user

The command will prompt for:
- Username
- Email
- Password
- Confirmation

Or use the environment-based defaults for non-interactive setup:
    python manage.py create_admin_user --no-input
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a default administrator user with full privileges'

    def add_arguments(self, parser):
        """Add optional arguments to the command."""
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username for the admin account (default: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@multiblizpos.com',
            help='Email for the admin account (default: admin@multiblizpos.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='Admin@123456',
            help='Password for the admin account (default: Admin@123456) - CHANGE THIS IN PRODUCTION!'
        )
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Create admin with default values without prompting'
        )

    def handle(self, *args, **options):
        """Execute the command to create admin user."""
        
        # Get parameters
        username = options['username']
        email = options['email']
        password = options['password']
        no_input = options['no_input']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"⚠ User '{username}' already exists. Skipping creation."
                )
            )
            return

        # Get input if not in no-input mode
        if not no_input:
            self.stdout.write(self.style.WARNING(
                "\n⚙ Creating Administrator Account\n"
            ))
            
            username = input(f"Username [default: {username}]: ").strip() or username
            
            # Check again after user input
            if User.objects.filter(username=username).exists():
                raise CommandError(f"User '{username}' already exists.")
            
            email = input(f"Email [default: {email}]: ").strip() or email
            
            while True:
                password = input(f"Password [default: Admin@123456]: ").strip() or password
                password_confirm = input("Confirm Password: ").strip()
                
                if password == password_confirm:
                    break
                else:
                    self.stdout.write(
                        self.style.ERROR("Passwords do not match. Try again.")
                    )

        # Create the admin user
        try:
            admin_user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            
            # Explicitly set the role to admin
            admin_user.role = 'admin'
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✓ Administrator account created successfully!\n"
                    f"  Username: {username}\n"
                    f"  Email: {email}\n"
                    f"  Role: Administrator (Full Access)\n"
                    f"  Status: Active\n"
                )
            )
            
            self.stdout.write(
                self.style.WARNING(
                    "\n⚠ SECURITY REMINDER:\n"
                    "  - Change the default password immediately after first login\n"
                    "  - Do not share admin credentials\n"
                    "  - Use strong passwords in production\n"
                )
            )

        except IntegrityError as e:
            raise CommandError(f"Failed to create user: {str(e)}")
        except Exception as e:
            raise CommandError(f"An error occurred: {str(e)}")
