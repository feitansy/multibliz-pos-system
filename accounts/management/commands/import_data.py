from django.core.management.base import BaseCommand
from django.core import serializers
from django.db import transaction
from django.apps import apps
import json
import os

class Command(BaseCommand):
    help = 'Import data from JSON file bundled with the app'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default='data_lean.json',
            help='JSON file to import from'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        # Check if file exists
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return
        
        # Skip import if data already exists
        from sales.models import Product, Sale
        from inventory.models import Stock
        
        if Product.objects.exists() or Sale.objects.exists() or Stock.objects.exists():
            self.stdout.write(self.style.WARNING('Data already exists in database - skipping import'))
            return
        
        self.stdout.write(f'Loading data from {file_path}...')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.stdout.write(f'Found {len(data)} objects to import')
        
        # Disable the auto-create stock signal
        from django.db.models.signals import post_save
        from inventory.models import create_stock_for_product
        
        # Disconnect the signal
        post_save.disconnect(create_stock_for_product, sender=apps.get_model('sales', 'Product'))
        self.stdout.write('Disabled auto-create stock signal')
        
        try:
            with transaction.atomic():
                # Group objects by model
                objects_by_model = {}
                for obj in data:
                    model_name = obj['model']
                    if model_name not in objects_by_model:
                        objects_by_model[model_name] = []
                    objects_by_model[model_name].append(obj)
                
                # Import order matters for foreign keys
                import_order = [
                    'inventory.supplier',
                    'sales.product',
                    'inventory.stock',
                    'sales.sale',
                ]
                
                # Import in order
                for model_name in import_order:
                    if model_name in objects_by_model:
                        objects = objects_by_model[model_name]
                        self.stdout.write(f'Importing {len(objects)} {model_name} objects...')
                        
                        # Skip if model already has data
                        app_label, model_label = model_name.split('.')
                        Model = apps.get_model(app_label, model_label)
                        
                        if Model.objects.exists():
                            self.stdout.write(self.style.WARNING(f'  Skipping - {model_name} already has data'))
                            continue
                        
                        # Deserialize and save
                        json_str = json.dumps(objects)
                        for obj in serializers.deserialize('json', json_str):
                            obj.save()
                        
                        self.stdout.write(self.style.SUCCESS(f'  Imported {len(objects)} objects'))
                
            self.stdout.write(self.style.SUCCESS('Data import completed successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Import failed: {e}'))
            raise
            
        finally:
            # Reconnect the signal
            post_save.connect(create_stock_for_product, sender=apps.get_model('sales', 'Product'))
            self.stdout.write('Re-enabled auto-create stock signal')
