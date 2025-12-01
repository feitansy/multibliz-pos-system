from django.core.management.base import BaseCommand
from sales.models import Product
from inventory.models import Stock


class Command(BaseCommand):
    help = 'Check for Stock integrity issues'

    def handle(self, *args, **options):
        # Check for products without stock records
        products_without_stock = Product.objects.filter(stock__isnull=True)
        if products_without_stock.exists():
            self.stdout.write(self.style.WARNING(f"Found {products_without_stock.count()} products without stock records"))
            for p in products_without_stock[:5]:
                self.stdout.write(f"  - {p.id}: {p.name}")
        else:
            self.stdout.write(self.style.SUCCESS("All products have stock records"))
        
        # Check for duplicate stock records
        from django.db.models import Count
        duplicates = Stock.objects.values('product').annotate(count=Count('id')).filter(count__gt=1)
        if duplicates.exists():
            self.stdout.write(self.style.WARNING(f"Found {duplicates.count()} products with duplicate stock records"))
            for d in duplicates[:5]:
                stocks = Stock.objects.filter(product_id=d['product'])
                self.stdout.write(f"  - Product {d['product']}: {stocks.count()} stock records")
        else:
            self.stdout.write(self.style.SUCCESS("No duplicate stock records found"))
        
        # Check total counts
        total_products = Product.objects.count()
        total_stocks = Stock.objects.count()
        self.stdout.write(f"\nTotals: {total_products} products, {total_stocks} stock records")
