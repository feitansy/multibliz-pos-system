from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from audit.utils import log_action, get_model_changes

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
        response = super().form_valid(form)
        
        # Audit log
        obj = self.object
        model_name = self.model._meta.verbose_name.title()
        log_action(
            self.request, 'CREATE', obj,
            object_name=f'{model_name}: {obj}',
            description=f'Created {model_name.lower()} "{obj}"',
            changes={field.replace('_', ' ').title(): {'old': '—', 'new': str(form.cleaned_data.get(field, ''))} for field in form.changed_data}
        )
        
        messages.success(self.request, f"{self.model._meta.verbose_name} created successfully.")
        return response

class InventoryUpdateMixin(InventoryMixin, UpdateView):
    def form_valid(self, form):
        # Capture changes before saving
        changes = get_model_changes(self.object, form)
        old_name = str(self.object)
        model_name = self.model._meta.verbose_name.title()
        
        response = super().form_valid(form)
        
        # Audit log
        changed_fields = ', '.join(changes.keys()) if changes else 'No fields'
        log_action(
            self.request, 'UPDATE', self.object,
            object_name=f'{model_name}: {self.object}',
            description=f'Updated {model_name.lower()} "{old_name}" — Changed: {changed_fields}',
            changes=changes,
        )
        
        messages.success(self.request, f"{self.model._meta.verbose_name} updated successfully.")
        return response

class InventoryDeleteMixin(InventoryMixin, DeleteView):
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        model_name = self.model._meta.verbose_name.title()
        obj_name = str(obj)
        
        # Audit log before deletion
        log_action(
            request, 'DELETE', obj,
            object_name=f'{model_name}: {obj_name}',
            description=f'Deleted {model_name.lower()} "{obj_name}"',
        )
        
        messages.success(self.request, f"{self.model._meta.verbose_name} deleted successfully.")
        return super().delete(request, *args, **kwargs)
