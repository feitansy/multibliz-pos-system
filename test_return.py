#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')
django.setup()

from sales.models import Sale, Return

# Get a random sale without an active return
sale = Sale.objects.exclude(returns__status__in=['pending', 'approved', 'completed']).first()

if sale:
    print(f"Creating return for Sale #{sale.id}...")
    return_obj = Return.objects.create(
        sale=sale,
        quantity_returned=1,
        reason='defective',
        reason_details='Test return',
        refund_amount=sale.product.price,
        refund_payment_method='cash',
        status='pending',
        processed_by='admin'
    )
    print(f"✓ Return #{return_obj.id} created successfully!")
    print(f"  Sale: #{sale.id} - {sale.product.name}")
    print(f"  Status: {return_obj.status}")
    print(f"  Refund Amount: ₱{return_obj.refund_amount}")
else:
    print("No sales available for returns")
