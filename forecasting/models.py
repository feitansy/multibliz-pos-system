from django.db import models
from django.utils import timezone
from datetime import timedelta


class Forecast(models.Model):
    product = models.ForeignKey('sales.Product', on_delete=models.CASCADE)
    forecast_date = models.DateField()
    predicted_quantity = models.PositiveIntegerField()
    algorithm_used = models.CharField(max_length=50, choices=[('xgboost', 'XGBoost'), ('prophet', 'Prophet')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Forecast for {self.product.name} on {self.forecast_date}"
    
    @property
    def predicted_revenue(self):
        """Calculate predicted revenue based on quantity and product price"""
        return self.predicted_quantity * self.product.price


class ForecastConfig(models.Model):
    """
    Singleton model to track forecast generation configuration and status.
    Stores when forecasts were last generated and the generation interval.
    """
    last_generated = models.DateTimeField(null=True, blank=True)
    generation_interval_days = models.PositiveIntegerField(default=30)
    auto_generate_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Forecast Configuration'
        verbose_name_plural = 'Forecast Configuration'
    
    def __str__(self):
        return f"Forecast Config (Last: {self.last_generated}, Interval: {self.generation_interval_days} days)"
    
    @classmethod
    def get_config(cls):
        """Get or create the singleton config instance"""
        config, created = cls.objects.get_or_create(pk=1)
        return config
    
    def should_generate(self):
        """Check if forecasts should be generated based on interval"""
        if not self.auto_generate_enabled:
            return False
        
        if self.last_generated is None:
            return True
        
        days_since_last = (timezone.now() - self.last_generated).days
        return days_since_last >= self.generation_interval_days
    
    def days_until_next_generation(self):
        """Calculate days until next scheduled generation"""
        if self.last_generated is None:
            return 0
        
        days_since_last = (timezone.now() - self.last_generated).days
        days_remaining = self.generation_interval_days - days_since_last
        return max(0, days_remaining)
    
    def mark_generated(self):
        """Mark forecasts as just generated"""
        self.last_generated = timezone.now()
        self.save()
