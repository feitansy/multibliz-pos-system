#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from sales.models import Return
import json

# Login as admin
client = Client()
User = get_user_model()
admin_user = User.objects.filter(is_superuser=True, is_staff=True).first()
print(f"Admin user: {admin_user.username}")

login = client.login(username=admin_user.username, password='admin123')
print(f"Login successful: {login}")

# Get return #10
return_obj = Return.objects.get(id=10)
print(f"Current status: {return_obj.status}")

# Try to update via POST
update_url = f'/sales/return/{return_obj.id}/update/'
print(f"Update URL: {update_url}")

# Test GET first
get_response = client.get(update_url)
print(f"GET response: {get_response.status_code}")

# Test POST update
post_data = {
    'status': 'completed',
    'refund_payment_method': 'cash',  
    'reason_details': 'Test update via script',
    'refund_amount': str(return_obj.refund_amount)
}

print(f"POST data: {post_data}")

post_response = client.post(update_url, post_data, follow=True)
print(f"POST response: {post_response.status_code}")
print(f"Redirect chain: {post_response.redirect_chain}")

# Check if updated
return_obj.refresh_from_db()
print(f"New status: {return_obj.status}")
print(f"Processed by: {return_obj.processed_by}")
print(f"Processed date: {return_obj.processed_date}")

if return_obj.status == 'completed':
    print("✅ Update successful!")
else:
    print("❌ Update failed")
    # Print any form errors from response
    if hasattr(post_response, 'context') and 'form' in post_response.context:
        form = post_response.context['form']
        if form.errors:
            print(f"Form errors: {form.errors}")