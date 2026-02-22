#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')
django.setup()

from django.test import Client
from sales.models import Return

# Login
client = Client()
client.login(username='admin', password='admin123')

# Get Return #8
return_obj = Return.objects.get(id=8)
print(f'Testing update for Return #{return_obj.id}')
print(f'Current status: {return_obj.status}')
print(f'Sale: #{return_obj.sale.id} - {return_obj.sale.product.name}')

# Test update to 'approved' status
form_data = {
    'status': 'approved',
    'refund_payment_method': 'cash',
    'reason_details': 'Test update',
    'refund_amount': float(return_obj.refund_amount),
}

response = client.post(f'/sales/return/{return_obj.id}/update/', form_data, follow=False)
print(f'\nResponse status: {response.status_code}')
print(f'Redirect location: {response.get("Location", "No redirect")}')

# Check if status was updated
return_obj.refresh_from_db()
print(f'New status: {return_obj.status}')

if response.status_code == 302:
    print('\n✓ Update successful and redirected!')
else:
    print('\n✗ Update failed - no redirect')
