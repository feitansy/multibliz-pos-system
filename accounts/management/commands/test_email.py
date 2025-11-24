from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from accounts.models import User


class Command(BaseCommand):
    help = 'Test email functionality by sending a test email'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Email address to send test email to'
        )

    def handle(self, *args, **options):
        email = options['email']
        
        self.stdout.write(f"Sending test email to {email}...")
        
        try:
            # Try to get a user or create test data
            user = User.objects.first()
            if not user:
                self.stdout.write(self.style.ERROR('No users found. Create a user first.'))
                return
            
            # Generate reset link
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            # Prepare email context
            context = {
                'user': user,
                'uid': uid,
                'token': token,
                'protocol': 'http',
                'domain': 'localhost:8000',
            }
            
            # Render email
            email_html = render_to_string('accounts/password_reset_email.html', context)
            
            # Send email
            send_mail(
                subject='Password Reset for Multibliz POS Account',
                message='Check console output for HTML email',
                from_email='noreply@multiblizpos.com',
                recipient_list=[email],
                html_message=email_html,
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS(f'✓ Email sent successfully to {email}'))
            self.stdout.write(self.style.SUCCESS('(Check console output above to see email content)'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error sending email: {str(e)}'))
