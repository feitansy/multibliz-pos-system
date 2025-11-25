import os
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')

import django
django.setup()

from django.core import serializers
from sales.models import Product, Sale
from inventory.models import Stock, Supplier

# Get product IDs that have sales
product_ids_with_sales = set(Sale.objects.values_list('product_id', flat=True).distinct())
print(f"Products with sales: {len(product_ids_with_sales)}")

# Get all data
suppliers = Supplier.objects.all()
products = Product.objects.filter(id__in=product_ids_with_sales)
stocks = Stock.objects.filter(product_id__in=product_ids_with_sales)
sales = Sale.objects.all()

print(f"Exporting: {suppliers.count()} suppliers, {products.count()} products, {stocks.count()} stocks, {sales.count()} sales")

# Serialize
data = []

# Add suppliers
for obj in serializers.deserialize('json', serializers.serialize('json', suppliers)):
    data.append({
        'model': 'inventory.supplier',
        'pk': obj.object.pk,
        'fields': json.loads(serializers.serialize('json', [obj.object]))[0]['fields']
    })

# Add products
for obj in serializers.deserialize('json', serializers.serialize('json', products)):
    data.append({
        'model': 'sales.product',
        'pk': obj.object.pk,
        'fields': json.loads(serializers.serialize('json', [obj.object]))[0]['fields']
    })

# Add stocks
for obj in serializers.deserialize('json', serializers.serialize('json', stocks)):
    data.append({
        'model': 'inventory.stock',
        'pk': obj.object.pk,
        'fields': json.loads(serializers.serialize('json', [obj.object]))[0]['fields']
    })

# Add sales
for obj in serializers.deserialize('json', serializers.serialize('json', sales)):
    data.append({
        'model': 'sales.sale',
        'pk': obj.object.pk,
        'fields': json.loads(serializers.serialize('json', [obj.object]))[0]['fields']
    })

# Write to file
with open('data_essential.json', 'w') as f:
    json.dump(data, f, indent=2, default=str)

print(f"Exported {len(data)} objects to data_essential.json")
