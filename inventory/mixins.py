from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages

class InventoryMixin:
    model = None
    template_name = None
    success_url = None

class InventoryListMixin(InventoryMixin, ListView):
    context_object_name = 'items'
    paginate_by = 25
    
    def get_queryset(self):
        from django.db.models import Q
        from django.db import models
        queryset = super().get_queryset()
        
        # Search filter
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(product__name__icontains=search_query) |
                Q(supplier__name__icontains=search_query) |
                Q(id__icontains=search_query)
            )
        
        # Category filter (filter by product category)
        category_filter = self.request.GET.get('category', '').strip()
        if category_filter:
            queryset = queryset.filter(product__category=category_filter)
        
        # Stock status filter
        stock_status = self.request.GET.get('stock_status', '').strip()
        if stock_status:
            if stock_status == 'no_stocks':
                queryset = queryset.filter(quantity=0)
            elif stock_status == 'critical':
                queryset = queryset.filter(quantity__gt=0, quantity__lte=models.F('reorder_level'))
            elif stock_status == 'warning':
                queryset = queryset.filter(quantity__gt=models.F('reorder_level'), quantity__lte=models.F('reorder_level') + 15)
            elif stock_status == 'healthy':
                queryset = queryset.filter(quantity__gt=models.F('reorder_level') + 15)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_stock_status'] = self.request.GET.get('stock_status', '')
        
        # Get all unique categories from products that have stock
        # Check if this is Stock model (has product foreign key)
        try:
            from inventory.models import Stock
            if self.model == Stock:
                all_categories = Stock.objects.values_list('product__category', flat=True).distinct().filter(product__category__isnull=False).exclude(product__category='')
                context['all_categories'] = sorted(set(all_categories))
            else:
                context['all_categories'] = []
        except:
            context['all_categories'] = []
        
        return context

class InventoryDetailMixin(InventoryMixin, DetailView):
    pass

class InventoryCreateMixin(InventoryMixin, CreateView):
    def form_valid(self, form):
        messages.success(self.request, f"{self.model._meta.verbose_name} created successfully.")
        return super().form_valid(form)

class InventoryUpdateMixin(InventoryMixin, UpdateView):
    def form_valid(self, form):
        messages.success(self.request, f"{self.model._meta.verbose_name} updated successfully.")
        return super().form_valid(form)

class InventoryDeleteMixin(InventoryMixin, DeleteView):
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, f"{self.model._meta.verbose_name} deleted successfully.")
        return super().delete(request, *args, **kwargs)
