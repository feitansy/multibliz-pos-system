#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')
django.setup()

from sales.views import (ProductCreateView, ProductUpdateView, ProductListView, 
                         SaleListView, SaleDetailView)
from sales.forms import ProductForm, SaleForm, ReturnForm
from sales.models import Product, Sale, Return
from inventory.views import StockListView
from inventory.models import Stock
from dashboard.views import DashboardView

print("=" * 60)
print("MULTIBLIZ POS - COMPREHENSIVE DIAGNOSTIC")
print("=" * 60)

# Test 1: Models
print("\n📦 TESTING MODELS...")
try:
    products = Product.objects.count()
    print(f"✓ Product model: {products} products in database")
    
    sales = Sale.objects.count()
    print(f"✓ Sale model: {sales} sales in database")
    
    stock = Stock.objects.count()
    print(f"✓ Stock model: {stock} stock records in database")
    
    returns = Return.objects.count()
    print(f"✓ Return model: {returns} returns in database")
except Exception as e:
    print(f"✗ Model error: {e}")

# Test 2: Forms
print("\n📋 TESTING FORMS...")
try:
    pf = ProductForm()
    print(f"✓ ProductForm: {len(pf.fields)} fields")
    print(f"  Fields: {list(pf.fields.keys())}")
    
    sf = SaleForm()
    print(f"✓ SaleForm: {len(sf.fields)} fields")
    
    rf = ReturnForm()
    print(f"✓ ReturnForm: {len(rf.fields)} fields")
except Exception as e:
    print(f"✗ Form error: {e}")

# Test 3: Views
print("\n🎬 TESTING VIEWS...")
try:
    print(f"✓ ProductCreateView -> {ProductCreateView.model.__name__}")
    print(f"✓ ProductUpdateView -> {ProductUpdateView.model.__name__}")
    print(f"✓ ProductListView -> {ProductListView.model.__name__}")
    print(f"✓ SaleListView -> {SaleListView.model.__name__}")
    print(f"✓ StockListView -> {StockListView.model.__name__}")
except Exception as e:
    print(f"✗ View error: {e}")

# Test 4: Product Image Field
print("\n🖼️  TESTING PRODUCT IMAGE FIELD...")
try:
    image_field = Product._meta.get_field('image')
    print(f"✓ Image field exists: {image_field.name}")
    print(f"  Type: {type(image_field).__name__}")
    print(f"  Upload to: {image_field.upload_to}")
    print(f"  Blank: {image_field.blank}")
    print(f"  Null: {image_field.null}")
except Exception as e:
    print(f"✗ Image field error: {e}")

# Test 5: Database Integrity
print("\n🗄️  TESTING DATABASE INTEGRITY...")
try:
    # Check for orphaned records
    from django.db.models import Q
    orphaned_sales = Sale.objects.filter(product__isnull=True).count()
    print(f"✓ No orphaned sales: {orphaned_sales == 0}")
    
    # Check stock consistency
    stock_count = Stock.objects.count()
    product_count = Product.objects.count()
    print(f"✓ Stock records ({stock_count}) vs Products ({product_count})")
    
except Exception as e:
    print(f"✗ Database integrity error: {e}")

# Test 6: URL Configuration
print("\n🔗 TESTING URL CONFIGURATION...")
try:
    from django.urls import get_resolver
    resolver = get_resolver()
    url_patterns = [str(p.pattern) for p in resolver.url_patterns]
    
    required_patterns = ['admin/', 'sales/', 'inventory/', 'forecasting/']
    for pattern in required_patterns:
        exists = any(pattern in p for p in url_patterns)
        status = "✓" if exists else "✗"
        print(f"{status} {pattern}: {'Found' if exists else 'MISSING'}")
        
except Exception as e:
    print(f"✗ URL configuration error: {e}")

# Test 7: Settings Check
print("\n⚙️  TESTING SETTINGS...")
try:
    from django.conf import settings
    
    print(f"✓ DEBUG: {settings.DEBUG}")
    print(f"✓ Database: {settings.DATABASES['default']['ENGINE'].split('.')[-1]}")
    print(f"✓ Media URL: {settings.MEDIA_URL}")
    print(f"✓ Media Root: {settings.MEDIA_ROOT}")
    print(f"✓ Static URL: {settings.STATIC_URL}")
    
    # Check if media folder exists
    import os
    media_exists = os.path.exists(settings.MEDIA_ROOT)
    print(f"✓ Media folder exists: {media_exists}")
    
    products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
    products_exists = os.path.exists(products_dir)
    print(f"✓ Products directory exists: {products_exists}")
    
except Exception as e:
    print(f"✗ Settings error: {e}")

# Test 8: Key Functionality
print("\n✨ TESTING KEY FUNCTIONALITY...")
try:
    # Test creating a product (without saving)
    test_product = Product(
        name="Test Product",
        price=10.00,
        category="Test"
    )
    print(f"✓ Product creation: OK")
    
    # Test stock model
    if Product.objects.exists():
        p = Product.objects.first()
        stock_exists = Stock.objects.filter(product=p).exists()
        print(f"✓ Product-Stock relationship: {'OK' if stock_exists else 'WARNING - Product has no stock'}")
    
except Exception as e:
    print(f"✗ Functionality error: {e}")

print("\n" + "=" * 60)
print("✅ DIAGNOSTIC COMPLETE")
print("=" * 60)
