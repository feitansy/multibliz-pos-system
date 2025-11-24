from django.db import models
from .models import Stock

def low_stock_notifications(request):
    """
    Context processor to add low stock notifications to all templates
    """
    if request.user.is_authenticated:
        # Get all low stock items
        low_stock_items = Stock.objects.filter(quantity__lte=models.F('reorder_level')).select_related('product')
        
        notifications = []
        for stock in low_stock_items:
            notifications.append({
                'type': 'warning',
                'icon': 'fa-exclamation-triangle',
                'title': f'Low Stock: {stock.product.name}',
                'message': f'Only {stock.quantity} units remaining (Reorder at {stock.reorder_level})',
                'url': f'/inventory/stocks/{stock.id}/',
                'timestamp': stock.last_updated
            })
        
        return {
            'low_stock_notifications': notifications,
            'notification_count': len(notifications)
        }
    
    return {
        'low_stock_notifications': [],
        'notification_count': 0
    }
