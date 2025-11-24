import os
import django
import pandas as pd
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')
django.setup()

from sales.models import Product, Sale

def import_superstore_data():
    """Import sales data from Sample - Superstore.csv into the database"""
    
    # Read the CSV file
    csv_path = 'training_ML/Sample - Superstore.csv'
    print(f"Reading {csv_path}...")
    df = pd.read_csv(csv_path, encoding='latin-1')
    
    print(f"Found {len(df)} sales records")
    print(f"Date range: {df['Order Date'].min()} to {df['Order Date'].max()}")
    
    # Track statistics
    products_created = 0
    sales_created = 0
    errors = 0
    
    # Process each row
    for index, row in df.iterrows():
        try:
            # Get or create product
            product_name = row['Product Name']
            category = row['Category']
            price = float(row['Sales']) / int(row['Quantity'])  # Calculate unit price
            
            product, created = Product.objects.get_or_create(
                name=product_name,
                defaults={
                    'description': f"{category} - {row['Sub-Category']}",
                    'price': round(price, 2),
                    'category': category
                }
            )
            
            if created:
                products_created += 1
            
            # Create sale record
            order_date = datetime.strptime(row['Order Date'], '%m/%d/%Y')
            quantity = int(row['Quantity'])
            total_price = float(row['Sales'])
            
            Sale.objects.create(
                product=product,
                quantity=quantity,
                total_price=total_price,
                sale_date=order_date,
                customer_name=row['Customer Name']
            )
            
            sales_created += 1
            
            if (index + 1) % 500 == 0:
                print(f"Processed {index + 1} records...")
                
        except Exception as e:
            errors += 1
            print(f"Error on row {index}: {e}")
            continue
    
    print("\n" + "="*50)
    print("IMPORT COMPLETE!")
    print("="*50)
    print(f"Products created: {products_created}")
    print(f"Sales records created: {sales_created}")
    print(f"Errors: {errors}")
    print(f"\nTotal products in database: {Product.objects.count()}")
    print(f"Total sales in database: {Sale.objects.count()}")

if __name__ == '__main__':
    print("Starting data import...")
    print("This will import sales data from Sample - Superstore.csv")
    
    response = input("Continue? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        import_superstore_data()
    else:
        print("Import cancelled.")
