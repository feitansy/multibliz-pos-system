#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')
django.setup()

from django.test import Client
from sales.models import Sale, Return

# Login
client = Client()
client.login(username='admin', password='admin123')

# Get a sale without active returns
sale = Sale.objects.exclude(returns__status__in=['pending', 'approved', 'completed']).first()
print(f'Testing with Sale #{sale.id}: {sale.product.name}')

form_data = {
    'sale': sale.id,
    'quantity_returned': 1,
    'reason': 'defective',
    'reason_details': 'Test after fix',
    'refund_amount': float(sale.product.price),
    'refund_payment_method': 'cash',
}

# Count returns before
returns_before = Return.objects.count()

response = client.post('/sales/return/create/', form_data, follow=False)
print(f'Response: {response.status_code}')
print(f'Redirect: {response.get("Location", "No redirect")}')

# Count returns after
returns_after = Return.objects.count()
print(f'\nReturns before: {returns_before}')
print(f'Returns after: {returns_after}')

if returns_after > returns_before:
    new_return = Return.objects.latest('id')
    print(f'✓ New return created: #{new_return.id}')
