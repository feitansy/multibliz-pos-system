#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from sales.models import Return

# Get the exact same data the browser is sending
client = Client()
User = get_user_model()
admin_user = User.objects.filter(is_superuser=True, is_staff=True).first()

# Login
client.login(username=admin_user.username, password='admin123')

# Get Return #3 
return_obj = Return.objects.get(id=3)
print(f"Return #3 current status: {return_obj.status}")

# Get the CSRF token from the response
get_response = client.get(f'/sales/return/{return_obj.id}/update/')
print(f"GET response status: {get_response.status_code}")

# Extract CSRF token from the HTML content
csrf_token = None
content = get_response.content.decode()
if 'csrfmiddlewaretoken' in content:
    import re
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', content)
    if match:
        csrf_token = match.group(1)

print(f"CSRF Token: {csrf_token}")

# Use the exact same data structure as the browser
form_data = {
    'csrfmiddlewaretoken': csrf_token,
    'status': 'rejected',
    'refund_payment_method': 'cash',
    'reason_details': '',
    'refund_amount': '3.75'
}

print(f"Submitting exact browser data: {form_data}")

try:
    # Submit with follow=True to see final result
    post_response = client.post(f'/sales/return/{return_obj.id}/update/', form_data, follow=True)
    print(f"POST response status: {post_response.status_code}")
    print(f"Final URL: {post_response.wsgi_request.path}")
    print(f"Redirect chain: {post_response.redirect_chain}")
    
    # Check if there are any form errors
    if hasattr(post_response, 'context') and post_response.context:
        if 'form' in post_response.context:
            form = post_response.context['form']
            if hasattr(form, 'errors') and form.errors:
                print(f"Form errors: {form.errors}")
                print(f"Form is valid: {form.is_valid()}")
        
        # Check for messages
        if 'messages' in post_response.context:
            messages = list(post_response.context['messages'])
            for msg in messages:
                print(f"Message: {msg.message} (Level: {msg.level_tag})")
    
    # Check final status
    return_obj.refresh_from_db()
    print(f"Final status: {return_obj.status}")
    
except Exception as e:
    print(f"Error during submission: {e}")
    import traceback
    traceback.print_exc()