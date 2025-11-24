"""
Clean Database - Remove Non-Printing Products
==============================================
This script removes products from the database that are not relevant
to a printing service business, keeping only printing-related items.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')
django.setup()

from sales.models import Product, Sale

print("=" * 80)
print("DATABASE CLEANUP - REMOVE NON-PRINTING PRODUCTS")
print("=" * 80)

# Define printing-relevant categories (case-insensitive matching)
PRINTING_CATEGORIES = [
    'OFFICE SUPPLIES',
    'PAPER',
    'BINDERS',
    'LABELS', 
    'ENVELOPES',
    'ART',
    'FASTENERS',
    'PRINTING',
    'BINDING',
    'STATIONERY',
]

# Keywords that indicate printing-relevant products
PRINTING_KEYWORDS = [
    'paper', 'xerox', 'bond', 'print', 'ink', 'toner', 'cartridge',
    'binder', 'binding', 'laminating', 'laminate',
    'label', 'sticker', 'envelope', 'staple', 'fastener',
    'pen', 'pencil', 'marker', 'highlighter', 'crayon',
    'folder', 'notepad', 'notebook', 'pad',
]

# Categories/keywords to REMOVE (non-printing items)
REMOVE_CATEGORIES = [
    'FURNITURE', 'TECHNOLOGY', 'APPLIANCES',
    'STORAGE', 'SHELVING', 'CABINET',
]

REMOVE_KEYWORDS = [
    'chair', 'table', 'desk', 'bookcase', 'shelf', 'shelving',
    'phone', 'computer', 'laptop', 'tablet', 'keyboard', 'mouse',
    'monitor', 'screen', 'projector', 'camera',
    'heater', 'fan', 'cleaner', 'purifier',
    'cart', 'trolley', 'file cart',
    'lamp', 'clock', 'telephone',
]

print("\n📊 CURRENT DATABASE STATUS")
print("-" * 80)
total_products = Product.objects.count()
total_sales = Sale.objects.count()
print(f"Total Products: {total_products}")
print(f"Total Sales: {total_sales}")

print("\n🔍 ANALYZING PRODUCTS...")
print("-" * 80)

# Analyze products
keep_products = []
remove_products = []

for product in Product.objects.all():
    product_name = product.name.lower()
    product_category = product.category.upper() if product.category else ''
    
    should_remove = False
    should_keep = False
    reason = ""
    
    # Check if it's in remove categories
    for cat in REMOVE_CATEGORIES:
        if cat in product_category:
            should_remove = True
            reason = f"Category: {cat}"
            break
    
    # Check if it has remove keywords
    if not should_remove:
        for keyword in REMOVE_KEYWORDS:
            if keyword in product_name:
                should_remove = True
                reason = f"Keyword: {keyword}"
                break
    
    # Check if it's in printing categories
    if not should_remove:
        for cat in PRINTING_CATEGORIES:
            if cat in product_category:
                should_keep = True
                reason = f"Category: {cat}"
                break
    
    # Check if it has printing keywords
    if not should_remove and not should_keep:
        for keyword in PRINTING_KEYWORDS:
            if keyword in product_name:
                should_keep = True
                reason = f"Keyword: {keyword}"
                break
    
    if should_remove:
        remove_products.append((product, reason))
    elif should_keep:
        keep_products.append((product, reason))
    else:
        # If uncertain, show for manual review
        remove_products.append((product, "Uncertain - likely not printing"))

print(f"\n✅ KEEP: {len(keep_products)} products (printing-relevant)")
print(f"❌ REMOVE: {len(remove_products)} products (non-printing)")

# Show sample of what will be removed
print("\n❌ SAMPLE PRODUCTS TO BE REMOVED (First 20):")
print("-" * 80)
for i, (product, reason) in enumerate(remove_products[:20], 1):
    print(f"{i:2d}. {product.name[:60]:60s} | {reason}")

# Show sample of what will be kept
print("\n✅ SAMPLE PRODUCTS TO BE KEPT (First 20):")
print("-" * 80)
for i, (product, reason) in enumerate(keep_products[:20], 1):
    print(f"{i:2d}. {product.name[:60]:60s} | {reason}")

print("\n" + "=" * 80)
print("⚠️  WARNING: This will DELETE products and their associated sales!")
print("=" * 80)
response = input("\nDo you want to proceed with deletion? (yes/no): ").strip().lower()

if response == 'yes':
    print("\n🗑️  DELETING NON-PRINTING PRODUCTS...")
    print("-" * 80)
    
    deleted_count = 0
    deleted_sales = 0
    
    for product, reason in remove_products:
        # Count associated sales
        sales_count = Sale.objects.filter(product=product).count()
        deleted_sales += sales_count
        
        # Delete product (sales will cascade delete)
        product.delete()
        deleted_count += 1
        
        if deleted_count % 100 == 0:
            print(f"  Deleted {deleted_count} products...")
    
    print(f"\n✅ CLEANUP COMPLETE!")
    print("-" * 80)
    print(f"Products deleted: {deleted_count}")
    print(f"Sales deleted: {deleted_sales}")
    print(f"Products remaining: {Product.objects.count()}")
    print(f"Sales remaining: {Sale.objects.count()}")
    
    print("\n📊 REMAINING PRODUCT CATEGORIES:")
    print("-" * 80)
    remaining_categories = Product.objects.values_list('category', flat=True).distinct()
    for cat in remaining_categories:
        count = Product.objects.filter(category=cat).count()
        print(f"  {cat}: {count} products")
    
else:
    print("\n❌ Cleanup cancelled. No changes made to database.")

print("\n" + "=" * 80)
