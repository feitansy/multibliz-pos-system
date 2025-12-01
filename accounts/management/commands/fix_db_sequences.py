from django.core.management.base import BaseCommand
from django.db import connection, DEFAULT_DB_ALIAS
from django.db.models import Max
from sales.models import Product
from inventory.models import Stock


class Command(BaseCommand):
    help = 'Fix PostgreSQL database sequences for auto-increment IDs'

    def handle(self, *args, **options):
        """Fix PostgreSQL sequences that got out of sync after data import"""
        
        # Check if this is PostgreSQL
        db_engine = connection.settings_dict.get('ENGINE', '')
        if 'postgresql' not in db_engine:
            self.stdout.write(self.style.WARNING("This command only works with PostgreSQL. Current DB: " + db_engine))
            return
        
        with connection.cursor() as cursor:
            # Fix sales_product sequence
            max_product_id = Product.objects.aggregate(max_id=Max('id'))['max_id'] or 0
            self.stdout.write(f"Max Product ID: {max_product_id}")
            
            cursor.execute(f"SELECT setval('sales_product_id_seq', {max_product_id} + 1);")
            self.stdout.write(self.style.SUCCESS(f"Set sales_product_id_seq to {max_product_id + 1}"))
            
            # Fix inventory_stock sequence
            max_stock_id = Stock.objects.aggregate(max_id=Max('id'))['max_id'] or 0
            self.stdout.write(f"Max Stock ID: {max_stock_id}")
            
            cursor.execute(f"SELECT setval('inventory_stock_id_seq', {max_stock_id} + 1);")
            self.stdout.write(self.style.SUCCESS(f"Set inventory_stock_id_seq to {max_stock_id + 1}"))
        
        self.stdout.write(self.style.SUCCESS("Database sequences fixed!"))
