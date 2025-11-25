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
            default='data_export.json',
            help='JSON file to import from'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        # Check if file exists
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return
        
        self.stdout.write(f'Loading data from {file_path}...')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.stdout.write(f'Found {len(data)} objects to import')
        
        # Disable signals temporarily
        from inventory.models import Stock
        from django.db.models.signals import post_save
        from inventory.signals import create_stock_for_product
        
        # Disconnect the signal
        post_save.disconnect(create_stock_for_product, sender=apps.get_model('inventory', 'Product'))
        
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
                    'accounts.user',
                    'inventory.supplier',
                    'inventory.product',
                    'inventory.stock',
                    'sales.sale',
                    'sales.saleitem',
                    'audit.auditlog',
                    'forecasting.forecastresult',
                    'dashboard.dashboardmetric',
                ]
                
                # Import in order
                for model_name in import_order:
                    if model_name in objects_by_model:
                        objects = objects_by_model[model_name]
                        self.stdout.write(f'Importing {len(objects)} {model_name} objects...')
                        
                        # Skip if model already has data (except for admin user)
                        app_label, model_label = model_name.split('.')
                        Model = apps.get_model(app_label, model_label)
                        
                        if model_name == 'accounts.user':
                            # Only import non-admin users
                            existing_usernames = set(Model.objects.values_list('username', flat=True))
                            objects = [o for o in objects if o['fields'].get('username') not in existing_usernames]
                            if not objects:
                                self.stdout.write(f'  Skipping - users already exist')
                                continue
                        elif Model.objects.exists():
                            self.stdout.write(f'  Skipping - {model_name} already has data')
                            continue
                        
                        # Deserialize and save
                        json_str = json.dumps(objects)
                        for obj in serializers.deserialize('json', json_str):
                            obj.save()
                        
                        self.stdout.write(self.style.SUCCESS(f'  Imported {len(objects)} objects'))
                
                # Import any remaining models
                imported = set(import_order)
                for model_name, objects in objects_by_model.items():
                    if model_name not in imported:
                        self.stdout.write(f'Importing {len(objects)} {model_name} objects...')
                        json_str = json.dumps(objects)
                        for obj in serializers.deserialize('json', json_str):
                            try:
                                obj.save()
                            except Exception as e:
                                self.stdout.write(self.style.WARNING(f'  Skipped object: {e}'))
                        
            self.stdout.write(self.style.SUCCESS('Data import completed successfully!'))
            
        finally:
            # Reconnect the signal
            post_save.connect(create_stock_for_product, sender=apps.get_model('inventory', 'Product'))
