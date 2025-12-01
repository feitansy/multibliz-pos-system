from django.db.models.signals import post_save
from django.dispatch import receiver
from sales.models import Return
from inventory.models import Stock
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Return)
def auto_process_return(sender, instance, created, update_fields, **kwargs):
    """
    Automatically process returns and adjust inventory when return status changes to 'completed'
    
    When a return is marked as 'completed':
    1. Add the returned quantity back to stock
    2. Log the inventory adjustment
    """
    
    # Only process if status changed to 'completed'
    if instance.status == 'completed':
        try:
            # Get the product from the sale
            product = instance.sale.product
            
            # Get the stock record
            stock = Stock.objects.get(product=product)
            
            # Add returned quantity back to stock
            old_quantity = stock.quantity
            stock.quantity += instance.quantity_returned
            stock.save()
            
            logger.info(
                f"Return #{instance.id} processed: "
                f"Product '{product.name}' stock updated from {old_quantity} to {stock.quantity} "
                f"(+{instance.quantity_returned} units returned)"
            )
            
        except Stock.DoesNotExist:
            logger.error(f"Stock record not found for product {product.id} when processing return #{instance.id}")
        except Exception as e:
            logger.error(f"Error processing return #{instance.id}: {str(e)}", exc_info=True)
