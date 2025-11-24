"""
Management command to clean up old forecasts
Run: python manage.py cleanup_forecasts
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from forecasting.models import Forecast
from datetime import timedelta

class Command(BaseCommand):
    help = 'Delete old forecasts (older than 60 days)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=60,
            help='Delete forecasts older than this many days (default: 60)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now().date() - timedelta(days=days)
        
        old_forecasts = Forecast.objects.filter(forecast_date__lt=cutoff_date)
        count = old_forecasts.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS(f'No forecasts older than {days} days found.'))
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would delete {count} forecasts older than {cutoff_date}')
            )
        else:
            old_forecasts.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {count} old forecasts (older than {cutoff_date})')
            )
