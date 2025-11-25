from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Stock(models.Model):
    product = models.OneToOneField('sales.Product', on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Stock for {self.product.name}: {self.quantity}"

    @property
    def is_low_stock(self):
        return self.quantity <= self.reorder_level

# Auto-create stock records for new products
@receiver(post_save, sender='sales.Product')
def create_stock_for_product(sender, instance, created, **kwargs):
    if created:
        Stock.objects.get_or_create(
            product=instance,
            defaults={'quantity': 0, 'reorder_level': 10}
        )
