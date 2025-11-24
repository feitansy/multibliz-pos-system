from django.db import models

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
