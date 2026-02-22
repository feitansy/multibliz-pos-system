#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')
django.setup()

from sales.models import Sale, Return
from inventory.models import Stock

# Get the last created return
return_obj = Return.objects.last()
sale = return_obj.sale
product = sale.product

print(f"Testing return approval for Return #{return_obj.id}")
print(f"Sale: #{sale.id} - {product.name}")
print(f"Quantity returned: {return_obj.quantity_returned} units")
print(f"Refund amount: ₱{return_obj.refund_amount}")

# Get current stock
stock = Stock.objects.get(product=product)
print(f"\n📊 Before approval:")
print(f"  Stock quantity: {stock.quantity} units")

# Approve the return
return_obj.status = 'approved'
return_obj.save()

# Refresh stock from database
stock.refresh_from_db()
print(f"\n✓ Return approved!")
print(f"📊 After approval:")
print(f"  Stock quantity: {stock.quantity} units")
print(f"  Change: +{return_obj.quantity_returned} units")

# Verify the sale properties
print(f"\n📋 Sale properties:")
print(f"  Has approved return: {sale.has_approved_return}")
print(f"  Total returned quantity: {sale.total_returned_quantity}")
print(f"  Total refunded amount: ₱{sale.total_refunded_amount}")
