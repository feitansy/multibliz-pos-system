from django.contrib import admin
from .models import Product, Sale, Return

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['-created_at']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'quantity', 'total_price', 'customer_name', 'sale_date']
    list_filter = ['sale_date', 'product']
    search_fields = ['customer_name', 'product__name']
    ordering = ['-sale_date']
    readonly_fields = ['sale_date']
    
    def has_delete_permission(self, request, obj=None):
        """Disable delete permission for all users - sales records cannot be deleted"""
        return False

@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = ['id', 'sale', 'quantity_returned', 'refund_amount', 'status', 'reason', 'return_date']
    list_filter = ['status', 'reason', 'return_date']
    search_fields = ['sale__id', 'sale__product__name', 'sale__customer_name', 'processed_by']
    ordering = ['-return_date']
    readonly_fields = ['return_date']
    
    fieldsets = (
        ('Return Information', {
            'fields': ('sale', 'quantity_returned', 'reason', 'reason_details')
        }),
        ('Financial', {
            'fields': ('refund_amount',)
        }),
        ('Status & Processing', {
            'fields': ('status', 'processed_by', 'processed_date', 'return_date')
        }),
    )
