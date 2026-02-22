#!/usr/bin/env python
"""
Test return form submission via Django test client
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')
django.setup()

from django.test import Client
from accounts.models import User
from sales.models import Sale, Return

# Get or create admin user
admin_user, _ = User.objects.get_or_create(username='admin', defaults={'is_staff': True, 'is_superuser': True})

# Create client and login
client = Client()
client.login(username='admin', password='admin123')

# Get a sale without an active return
sale = Sale.objects.exclude(returns__status__in=['pending', 'approved', 'completed']).first()

if sale:
    print(f"Testing form submission for Sale #{sale.id}...")
    
    # Prepare form data
    form_data = {
        'sale': sale.id,
        'quantity_returned': 1,
        'reason': 'defective',
        'reason_details': 'Form submission test',
        'refund_amount': float(sale.product.price),
        'refund_payment_method': 'cash',
    }
    
    print(f"Form data: {form_data}")
    
    # Submit form
    response = client.post('/sales/return/create/', form_data, follow=True)
    
    print(f"Status code: {response.status_code}")
    print(f"Redirected: {response.redirect_chain}")
    
    # Check if return was created
    last_return = Return.objects.last()
    if last_return and last_return.sale.id == sale.id:
        print(f"✓ Return #{last_return.id} created successfully!")
        print(f"  Status: {last_return.status}")
        print(f"  Refund Amount: ₱{last_return.refund_amount}")
        print(f"  Refund Method: {last_return.refund_payment_method}")
    else:
        print("✗ Return creation failed")
        print(f"Response content preview: {response.content[:500]}")
else:
    print("No sales available for testing")
