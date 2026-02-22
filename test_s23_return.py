#!/usr/bin/env python
import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')
django.setup()

from django.test import Client
from sales.models import Sale

# Login as admin
client = Client()
client.login(username='admin', password='admin123')

# Test with Sale #10531
sale = Sale.objects.get(id=10531)
print(f'Testing with Sale #{sale.id}: {sale.product.name}')

# Submit form with exact data
form_data = {
    'sale': 10531,
    'quantity_returned': 1,
    'reason': 'defective',
    'reason_details': 'Browser test',
    'refund_amount': float(sale.total_price),
    'refund_payment_method': 'cash',
}

print(f'Submitting form with data: {form_data}')

response = client.post('/sales/return/create/', form_data, follow=False)
print(f'\nResponse status: {response.status_code}')
print(f'Location: {response.get("Location", "No redirect")}')

if response.status_code == 200:
    content = response.content.decode()
    if 'errorlist' in content:
        print('\nForm errors found:')
        errors = re.findall(r'<li>(.*?)</li>', content)
        for error in errors[:10]:
            print(f'  - {error}')
    else:
        print('\nNo form errors visible')
        
        # Check if there's a non-field error
        if 'This field is required' in content:
            print('Found "This field is required" error')
        if 'error' in content.lower():
            print('Found error-related content')
else:
    print('Form submitted successfully!')
