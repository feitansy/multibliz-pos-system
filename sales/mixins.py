from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import models, transaction
from inventory.models import Stock

class ProductMixin:
    model = None  # To be set in subclasses
    template_name = None
    success_url = None

class ProductListMixin(ProductMixin, ListView):
    context_object_name = 'products'
    paginate_by = 25
    
    def get_queryset(self):
        from django.db.models import Q
        from inventory.models import Stock
        
        queryset = super().get_queryset()
        
        # Search filter
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(category__icontains=search_query) |
                Q(id__icontains=search_query)
            )
        
        # Category filter
        category_filter = self.request.GET.get('category', '').strip()
        if category_filter:
            queryset = queryset.filter(category=category_filter)
        
        # Stock status filter
        stock_status = self.request.GET.get('stock_status', '').strip()
        if stock_status:
            if stock_status == 'no_stocks':
                # Get products with NO STOCKS (quantity = 0)
                no_stock_products = Stock.objects.filter(quantity=0).values_list('product_id', flat=True)
                queryset = queryset.filter(id__in=no_stock_products)
            elif stock_status == 'critical':
                # Get products with critical stock (0 < quantity <= reorder_level)
                critical_products = Stock.objects.filter(quantity__gt=0, quantity__lte=models.F('reorder_level')).values_list('product_id', flat=True)
                queryset = queryset.filter(id__in=critical_products)
            elif stock_status == 'warning':
                # Get products with warning stock (quantity > reorder_level but <= reorder_level + 15)
                warning_products = Stock.objects.filter(
                    quantity__gt=models.F('reorder_level'),
                    quantity__lte=models.F('reorder_level') + 15
                ).values_list('product_id', flat=True)
                queryset = queryset.filter(id__in=warning_products)
            elif stock_status == 'healthy':
                # Get products with healthy stock (quantity > reorder_level + 15)
                healthy_products = Stock.objects.filter(
                    quantity__gt=models.F('reorder_level') + 15
                ).values_list('product_id', flat=True)
                queryset = queryset.filter(id__in=healthy_products)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_stock_status'] = self.request.GET.get('stock_status', '')
        
        # Get all unique categories from Product model
        all_categories = self.model.objects.values_list('category', flat=True).distinct().filter(category__isnull=False).exclude(category='')
        context['all_categories'] = sorted(all_categories)
        
        return context

class ProductDetailMixin(ProductMixin, DetailView):
    pass

class ProductCreateMixin(ProductMixin, CreateView):
    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Save the product first (also triggers signal to create Stock)
                response = super().form_valid(form)
                
                # Update the auto-created stock record with the supplier
                supplier = form.cleaned_data.get('supplier')
                if supplier:
                    try:
                        stock = Stock.objects.select_for_update().get(product=self.object)
                        stock.supplier = supplier
                        stock.save()
                    except Stock.DoesNotExist:
                        # Stock should be auto-created by signal, but just in case
                        Stock.objects.create(product=self.object, supplier=supplier)
                
                messages.success(self.request, f"{self.model._meta.verbose_name} created successfully.")
                return response
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating product: {str(e)}", exc_info=True)
            messages.error(self.request, f"Error creating product: {str(e)}")
            # Return to form with errors
            form.add_error(None, str(e))
            return self.form_invalid(form)

class ProductUpdateMixin(ProductMixin, UpdateView):
    def get_initial(self):
        initial = super().get_initial()
        # Pre-populate supplier field from Stock model
        try:
            stock = Stock.objects.get(product=self.object)
            initial['supplier'] = stock.supplier
        except Stock.DoesNotExist:
            pass
        return initial
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Update stock record with the supplier
        supplier = form.cleaned_data.get('supplier')
        try:
            stock = Stock.objects.get(product=self.object)
            stock.supplier = supplier
            stock.save()
        except Stock.DoesNotExist:
            Stock.objects.create(product=self.object, supplier=supplier)
        
        messages.success(self.request, f"{self.model._meta.verbose_name} updated successfully.")
        return response

class ProductDeleteMixin(ProductMixin, DeleteView):
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, f"{self.model._meta.verbose_name} deleted successfully.")
        return super().delete(request, *args, **kwargs)
