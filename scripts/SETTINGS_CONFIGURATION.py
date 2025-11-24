# ============================================
# SETTINGS.PY CONFIGURATION FOR OTP SYSTEM
# ============================================
# Copy these settings to your settings.py file

# ============================================
# EMAIL CONFIGURATION (Gmail SMTP)
# ============================================
# ✅ ALREADY CONFIGURED IN YOUR PROJECT!

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'multiblizinternationalcorp@gmail.com'
EMAIL_HOST_PASSWORD = 'jagr lpgc ztjq uvuh'  # Gmail App Password
DEFAULT_FROM_EMAIL = 'multiblizinternationalcorp@gmail.com'

# Note: If you want to use a different email service:
# 
# For SendGrid:
# EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
# SENDGRID_API_KEY = 'your-sendgrid-api-key'
# DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'
#
# For other SMTP servers:
# EMAIL_HOST = 'smtp.yourprovider.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'your-email@domain.com'
# EMAIL_HOST_PASSWORD = 'your-password'

# ============================================
# TWILIO SMS CONFIGURATION
# ============================================
# ⚠️ NEEDS TO BE CONFIGURED!
# Get credentials from: https://www.twilio.com/console

# Step 1: Sign up for Twilio (free trial available)
# Step 2: Get these values from Twilio Console:

TWILIO_ACCOUNT_SID = 'YOUR_TWILIO_ACCOUNT_SID'  # Replace with your Account SID
TWILIO_AUTH_TOKEN = 'YOUR_TWILIO_AUTH_TOKEN'   # Replace with your Auth Token
TWILIO_PHONE_NUMBER = '+1234567890'            # Replace with your Twilio phone number

# PRODUCTION VALUES (replace above with your actual values):
# Get these from https://www.twilio.com/console
# TWILIO_ACCOUNT_SID starts with 'AC' followed by 32 characters
# TWILIO_AUTH_TOKEN is a 32 character string
# TWILIO_PHONE_NUMBER format: +[country code][number]

# For Trial Accounts:
# - You can only send to verified phone numbers
# - Verify numbers at: https://www.twilio.com/console/phone-numbers/verified
# - Messages will include "Sent from a Twilio trial account"

# For Production (Paid Account):
# - Can send to any number
# - No trial message
# - Pay per SMS (~$0.0075 per message)

# ============================================
# DEVELOPMENT VS PRODUCTION
# ============================================

# DEVELOPMENT (Console backend - prints emails to console instead of sending):
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# PRODUCTION (SMTP backend - actually sends emails):
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# ============================================
# TESTING YOUR CONFIGURATION
# ============================================

# Test Email in Django Shell:
"""
python manage.py shell

from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Email',
    'This is a test message from Multibliz POS.',
    settings.DEFAULT_FROM_EMAIL,
    ['your-email@example.com'],
    fail_silently=False,
)
"""

# Test SMS in Django Shell:
"""
python manage.py shell

from twilio.rest import Client
from django.conf import settings

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

message = client.messages.create(
    body='Test SMS from Multibliz POS',
    from_=settings.TWILIO_PHONE_NUMBER,
    to='+1234567890'  # Your phone number (must be verified for trial)
)

print(f"SMS sent! SID: {message.sid}")
"""

# ============================================
# SECURITY BEST PRACTICES
# ============================================

# 1. Use Environment Variables (production):
"""
import os

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
"""

# 2. Never commit credentials to Git
# Add to .gitignore:
"""
.env
*.secret
settings_local.py
"""

# 3. Use django-environ for easier config management:
"""
pip install django-environ

# settings.py
import environ
env = environ.Env()
environ.Env.read_env()

EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
TWILIO_ACCOUNT_SID = env('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = env('TWILIO_AUTH_TOKEN')
"""
