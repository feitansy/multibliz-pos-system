#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from sales.models import Return
from django.urls import reverse

# Create client and login
client = Client()
User = get_user_model()
admin_user = User.objects.filter(is_superuser=True).first()
print(f"Admin user: {admin_user.username}")

# Login
login_success = client.login(username=admin_user.username, password='admin123')
print(f"Login successful: {login_success}")

# Get Return #9
try:
    return_obj = Return.objects.get(id=9)
    print(f'Testing Return #{return_obj.id}')
    print(f'Current status: {return_obj.status}')
    print(f'Sale: #{return_obj.sale.id} - {return_obj.sale.product.name}')
    
    # Test the GET request first
    url = f'/sales/return/{return_obj.id}/update/'
    print(f'Update URL: {url}')
    
    get_response = client.get(url)
    print(f'GET response status: {get_response.status_code}')
    
    if get_response.status_code == 200:
        print('✓ GET request successful')
        
        # Test POST with form data
        form_data = {
            'status': 'completed',
            'refund_payment_method': 'cash',
            'reason_details': 'Test completed update',
            'refund_amount': str(return_obj.refund_amount),
        }
        
        print(f'Form data: {form_data}')
        
        post_response = client.post(url, form_data, follow=False)
        print(f'POST response status: {post_response.status_code}')
        print(f'Response headers: {dict(post_response.items())}')
        
        if post_response.status_code == 302:
            print(f'Redirect location: {post_response["Location"]}')
            
            # Follow redirect
            follow_response = client.get(post_response["Location"])
            print(f'Follow response status: {follow_response.status_code}')
        
        # Check if status was updated
        return_obj.refresh_from_db()
        print(f'New status after POST: {return_obj.status}')
        
        if post_response.status_code == 302:
            print('\n✓ Form submission successful (redirected)!')
        else:
            print('\n✗ Form submission failed')
            print(f'Response content: {post_response.content[:500]}')
    else:
        print('✗ GET request failed')

except Return.DoesNotExist:
    print('Return #9 not found')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()