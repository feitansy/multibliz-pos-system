from django.db import models

class DashboardMetric(models.Model):
    metric_name = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.metric_name}: {self.value} on {self.date}"
