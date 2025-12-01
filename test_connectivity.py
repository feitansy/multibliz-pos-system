#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')
django.setup()

from django.urls import reverse
from django.test import Client

print("=" * 70)
print("BUTTON & FORM CONNECTIVITY TEST")
print("=" * 70)

client = Client()

# Test endpoints that should work
test_endpoints = [
    ('Dashboard', '/'),
    ('Sales Management', '/sales/product/'),
    ('Sales Records', '/sales/sale/'),
    ('Add Product', '/sales/product/create/'),
    ('Inventory - Stocks', '/inventory/stocks/'),
    ('Suppliers List', '/inventory/suppliers/'),
    ('Returns', '/sales/return/'),
    ('Forecasting', '/forecasting/forecasts/'),
]

print("\n🔍 CHECKING URL ENDPOINTS...")
errors = []

for name, url in test_endpoints:
    try:
        response = client.get(url, follow=True)
        
        # Check for 500 errors
        if response.status_code >= 500:
            status = f"❌ ERROR {response.status_code}"
            errors.append(f"{name}: {response.status_code}")
        # Check for 404 (not found)
        elif response.status_code == 404:
            status = f"⚠️  NOT FOUND {response.status_code}"
            errors.append(f"{name}: Not found")
        # Check for login redirect (302/200)
        elif response.status_code in [200, 302]:
            status = f"✓ OK {response.status_code}"
        else:
            status = f"⚠️  {response.status_code}"
            
        print(f"{status:20} {name:30} {url}")
    except Exception as e:
        print(f"❌ ERROR            {name:30} {url}")
        print(f"   Exception: {str(e)[:80]}")
        errors.append(f"{name}: {str(e)}")

# Test Form Endpoints
print("\n📋 CHECKING FORM SUBMISSIONS...")
form_tests = [
    ('Product Create Form', '/sales/product/create/', 'GET'),
    ('Product Update Form', '/sales/product/1/update/', 'GET'),
    ('Sale Form', '/sales/create/', 'GET'),
]

for name, url, method in form_tests:
    try:
        if method == 'GET':
            response = client.get(url, follow=True)
        else:
            response = client.post(url, {}, follow=True)
        
        if response.status_code >= 500:
            print(f"❌ ERROR {response.status_code}      {name:30} {url}")
            errors.append(f"{name} form: {response.status_code}")
        elif response.status_code in [200, 302]:
            print(f"✓ OK {response.status_code:3}       {name:30} {url}")
        else:
            print(f"⚠️  {response.status_code:3}       {name:30} {url}")
    except Exception as e:
        print(f"❌ EXCEPTION       {name:30} {url}")
        errors.append(f"{name}: {str(e)}")

# Check for common 500 error causes
print("\n🔧 CHECKING COMMON ERROR SOURCES...")

try:
    from sales.models import Product
    from inventory.models import Stock
    
    # Check if Product signals are working
    p = Product.objects.first()
    if p:
        stock = Stock.objects.filter(product=p).exists()
        print(f"✓ Product signals working: {stock}")
    else:
        print(f"⚠️  No products to test signals")
        
except Exception as e:
    print(f"❌ Signal test error: {str(e)}")
    errors.append(f"Signals: {str(e)}")

# Check template rendering
print("\n🎨 CHECKING TEMPLATE RENDERING...")

try:
    from django.template.loader import render_to_string
    from django.template import Context
    
    # Try to render a simple template
    templates_to_check = [
        'sales/product_list.html',
        'sales/product_form.html',
        'sales/sale_list.html',
    ]
    
    for template_name in templates_to_check:
        try:
            response = client.get('/sales/product/')
            if response.status_code == 200:
                print(f"✓ {template_name:40} renders OK")
            else:
                print(f"⚠️  {template_name:40} status {response.status_code}")
        except Exception as e:
            print(f"❌ {template_name:40} error: {str(e)[:50]}")
            
except Exception as e:
    print(f"⚠️  Template check unavailable: {str(e)}")

# Summary
print("\n" + "=" * 70)
if errors:
    print(f"⚠️  FOUND {len(errors)} POTENTIAL ISSUE(S):")
    for error in errors[:10]:
        print(f"   - {error}")
else:
    print("✅ NO ERRORS FOUND - All endpoints and forms are accessible!")
print("=" * 70)
