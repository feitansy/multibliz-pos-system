from django.db import models
from multibliz_pos.storage import ProductImageStorage

class Product(models.Model):
    name = models.CharField(max_length=255)
    label = models.CharField(max_length=255, blank=True, help_text="Receipt label/SKU for this product")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, blank=True)
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        help_text="Product image",
        storage=ProductImageStorage()
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Sale(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('check', 'Check'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    receipt_label = models.CharField(max_length=255, blank=True, help_text="Custom label for receipt")
    sale_date = models.DateTimeField(auto_now_add=True)
    transaction_date = models.DateField(null=True, blank=True, help_text="Custom date for old sales")
    customer_name = models.CharField(max_length=255, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    change_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Sale #{self.id} - {self.product.name} ({self.quantity} units) - ₱{self.total_price}"
    
    @property
    def has_approved_return(self):
        """Check if this sale has any approved or completed returns"""
        return self.returns.filter(status__in=['approved', 'completed']).exists()
    
    @property
    def total_returned_quantity(self):
        """Get total quantity returned for this sale (approved/completed only)"""
        from django.db.models import Sum
        result = self.returns.filter(status__in=['approved', 'completed']).aggregate(
            total=Sum('quantity_returned')
        )['total']
        return result or 0
    
    @property
    def total_refunded_amount(self):
        """Get total refund amount for this sale (approved/completed only)"""
        from django.db.models import Sum
        result = self.returns.filter(status__in=['approved', 'completed']).aggregate(
            total=Sum('refund_amount')
        )['total']
        return result or 0
    
    @property
    def net_total(self):
        """Get net total after returns"""
        return self.total_price - self.total_refunded_amount

class Return(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    REASON_CHOICES = [
        ('defective', 'Defective Product'),
        ('wrong_item', 'Wrong Item'),
        ('damaged', 'Damaged'),
        ('not_satisfied', 'Customer Not Satisfied'),
        ('other', 'Other'),
    ]
    
    REFUND_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('check', 'Check'),
    ]
    
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='returns')
    return_date = models.DateTimeField(auto_now_add=True)
    quantity_returned = models.PositiveIntegerField()
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    reason_details = models.TextField(blank=True, help_text="Additional details about the return")
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    refund_payment_method = models.CharField(max_length=20, choices=REFUND_METHOD_CHOICES, default='cash')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processed_by = models.CharField(max_length=255, blank=True)
    processed_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Return #{self.id} - Sale #{self.sale.id} - {self.get_status_display()}"
    
    class Meta:
        ordering = ['-return_date']
