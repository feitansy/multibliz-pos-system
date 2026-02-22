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

# Get the form page first
response = client.get('/sales/return/create/')
print(f'GET form page: {response.status_code}')

# Get a sale
sale = Sale.objects.exclude(returns__status__in=['pending', 'approved', 'completed']).first()
print(f'\nTesting with Sale #{sale.id}')

# Submit form with valid data
form_data = {
    'sale': sale.id,
    'quantity_returned': 1,
    'reason': 'defective',
    'reason_details': 'Browser test',
    'refund_amount': float(sale.product.price),
    'refund_payment_method': 'cash',
}

response = client.post('/sales/return/create/', form_data, follow=False)
print(f'POST form: {response.status_code}')
print(f'Location: {response.get("Location", "No redirect")}')

# Check response content for errors
if response.status_code == 200:
    content = response.content.decode()
    if 'errorlist' in content:
        print('\nForm errors found in response:')
        # Extract error text
        errors = re.findall(r'<li>(.*?)</li>', content)
        for error in errors[:10]:
            print(f'  - {error}')
    else:
        print('\nNo form errors visible in response')
        print(f'Response length: {len(content)} chars')
elif response.status_code == 302:
    print('\n✓ Form submitted successfully and redirected!')
else:
    print(f'\nUnexpected status code: {response.status_code}')
