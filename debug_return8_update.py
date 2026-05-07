#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from sales.models import Return
from sales.forms import ReturnForm

# Login as admin
client = Client()
User = get_user_model()
admin_user = User.objects.filter(is_superuser=True, is_staff=True).first()
client.login(username=admin_user.username, password='admin123')

# Get return #8
return_obj = Return.objects.get(id=8)
print(f"Return #8 current status: {return_obj.status}")
print(f"Refund amount: {return_obj.refund_amount}")

# Test the form with the same data being submitted
form_data = {
    'status': 'completed',
    'refund_payment_method': 'cash',  
    'reason_details': 'Test update',
    'refund_amount': '50000.00'  # Same as in the form
}

print(f"Testing form with data: {form_data}")

# Test the form validation directly
from django.forms.models import model_to_dict
initial_data = model_to_dict(return_obj)
print(f"Initial model data: {initial_data}")

# Create form instance like the view would
form = ReturnForm(data=form_data, instance=return_obj)
print(f"Form is valid: {form.is_valid()}")

if not form.is_valid():
    print(f"Form errors: {form.errors}")
else:
    print("Form validation passed")
    # Try to save
    try:
        saved_instance = form.save()
        print(f"Form saved successfully")
        print(f"New status: {saved_instance.status}")
        print(f"New refund amount: {saved_instance.refund_amount}")
    except Exception as e:
        print(f"Error saving form: {e}")

# Test via POST request
print("\n--- Testing POST request ---")
post_response = client.post(f'/sales/return/{return_obj.id}/update/', form_data, follow=True)
print(f"POST response status: {post_response.status_code}")
print(f"Redirect chain: {post_response.redirect_chain}")

# Check if context has form errors
if hasattr(post_response, 'context') and post_response.context and 'form' in post_response.context:
    form_in_context = post_response.context['form']
    if hasattr(form_in_context, 'errors') and form_in_context.errors:
        print(f"Form errors in response: {form_in_context.errors}")

# Check final status
return_obj.refresh_from_db()
print(f"Final status: {return_obj.status}")