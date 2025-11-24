import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')
django.setup()

from sales.models import Sale, Product
from accounts.models import User
from datetime import datetime, timedelta
import random

print("=" * 60)
print("GENERATING REALISTIC HISTORICAL SALES DATA")
print("=" * 60)

# Get products and a user
products = list(Product.objects.all()[:30])  # Use first 30 products
try:
    user = User.objects.filter(is_staff=True).first()
    if not user:
        user = User.objects.first()
except:
    print("Error: No users found. Please create a user first.")
    exit(1)

if not products:
    print("Error: No products found. Please create products first.")
    exit(1)

print(f"\nGenerating sales for {len(products)} products over 60 days...")
print(f"Using user: {user.username}")

# Generate sales for the past 60 days
sales_created = 0
today = datetime.now().date()

for days_ago in range(60, 0, -1):
    sale_date = datetime.combine(today - timedelta(days=days_ago), datetime.min.time())
    
    # Generate 3-10 sales per day
    num_sales = random.randint(3, 10)
    
    for _ in range(num_sales):
        # Pick a random product
        product = random.choice(products)
        
        # Random quantity (1-8 units, weighted towards lower values)
        quantity = random.choices([1, 2, 3, 4, 5, 6, 7, 8], 
                                 weights=[25, 20, 15, 15, 10, 8, 5, 2])[0]
        
        # Create sale
        sale = Sale(
            product=product,
            quantity=quantity,
            total_price=product.price * quantity,
            customer_name=f"Customer {random.randint(1, 100)}"
        )
        # Override the auto_now_add for sale_date
        sale.save()
        Sale.objects.filter(id=sale.id).update(sale_date=sale_date)
        sales_created += 1

print(f"\n✓ Created {sales_created} realistic sales over 60 days")

# Show statistics
from django.db.models import Sum, Avg, Count
from django.db.models.functions import TruncDate

stats = Sale.objects.aggregate(
    total_qty=Sum('quantity'),
    avg_qty=Avg('quantity'),
    total_sales=Count('id')
)

print("\n" + "=" * 60)
print("SALES DATA SUMMARY")
print("=" * 60)
print(f"Total sales: {stats['total_sales']}")
print(f"Total quantity: {stats['total_qty']} units")
print(f"Average per sale: {stats['avg_qty']:.2f} units")

# Sales by recent dates
recent_dates = Sale.objects.filter(
    sale_date__date__gte=today - timedelta(days=10)
).annotate(
    date=TruncDate('sale_date')
).values('date').annotate(
    daily_qty=Sum('quantity'),
    daily_count=Count('id')
).order_by('-date')[:10]

print("\nLast 10 days:")
for item in recent_dates:
    print(f"  {item['date']}: {item['daily_qty']} units ({item['daily_count']} sales)")

print("\n" + "=" * 60)
print("READY FOR FORECASTING!")
print("=" * 60)
print("\nNow you can:")
print("1. Go to the Forecasting page")
print("2. Click 'Generate Forecasts'")
print("3. AI will train on 60 days of realistic sales patterns")
print("\n" + "=" * 60)
