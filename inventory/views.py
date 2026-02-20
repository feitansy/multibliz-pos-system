from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum, F, Value
from django.db.models.functions import Coalesce
from datetime import datetime
from .models import Supplier, Stock
from .forms import StockForm, SupplierForm
from .mixins import InventoryListMixin, InventoryDetailMixin, InventoryCreateMixin, InventoryUpdateMixin, InventoryDeleteMixin
from audit.utils import log_action

class SupplierListView(LoginRequiredMixin, InventoryListMixin):
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    success_url = reverse_lazy('supplier_list')

class SupplierDetailView(LoginRequiredMixin, InventoryDetailMixin):
    model = Supplier
    template_name = 'inventory/supplier_detail.html'

class SupplierCreateView(LoginRequiredMixin, InventoryCreateMixin):
    model = Supplier
    template_name = 'inventory/supplier_form.html'
    form_class = SupplierForm
    success_url = reverse_lazy('supplier_list')

class SupplierUpdateView(LoginRequiredMixin, InventoryUpdateMixin):
    model = Supplier
    template_name = 'inventory/supplier_form.html'
    form_class = SupplierForm
    success_url = reverse_lazy('supplier_list')

class SupplierDeleteView(LoginRequiredMixin, InventoryDeleteMixin):
    model = Supplier
    template_name = 'inventory/supplier_confirm_delete.html'
    success_url = reverse_lazy('supplier_list')

class StockListView(LoginRequiredMixin, InventoryListMixin):
    model = Stock
    template_name = 'inventory/stock_list.html'
    success_url = reverse_lazy('stock_list')

class StockDetailView(LoginRequiredMixin, InventoryDetailMixin):
    model = Stock
    template_name = 'inventory/stock_detail.html'

class StockCreateView(LoginRequiredMixin, CreateView):
    """
    Stock Create View - Add stock to products
    If product already has stock, it updates the existing stock record.
    If product has no stock, it creates a new stock record.
    """
    model = Stock
    template_name = 'inventory/stock_form.html'
    form_class = StockForm
    success_url = reverse_lazy('stock_list')
    
    def form_valid(self, form):
        product = form.cleaned_data.get('product')
        quantity = form.cleaned_data.get('quantity')
        supplier = form.cleaned_data.get('supplier')
        reorder_level = form.cleaned_data.get('reorder_level')
        
        # Check if stock already exists for this product
        try:
            existing_stock = Stock.objects.get(product=product)
            old_quantity = existing_stock.quantity
            # Update existing stock - ADD the new quantity to existing
            existing_stock.quantity += quantity
            if supplier:
                existing_stock.supplier = supplier
            if reorder_level:
                existing_stock.reorder_level = reorder_level
            existing_stock.save()
            
            # Audit log
            log_action(
                self.request, 'UPDATE', existing_stock,
                object_name=f'Stock: {product.name}',
                description=f'Restocked "{product.name}" — Added {quantity} units (was {old_quantity}, now {existing_stock.quantity})',
                changes={
                    'Quantity': {'old': str(old_quantity), 'new': str(existing_stock.quantity)},
                    'Units Added': {'old': '—', 'new': str(quantity)},
                    'Supplier': {'old': '—', 'new': str(supplier) if supplier else 'N/A'},
                }
            )
            
            messages.success(self.request, f"Added {quantity} units to {product.name}. New total: {existing_stock.quantity} units.")
            return redirect(self.success_url)
        except Stock.DoesNotExist:
            # Create new stock record
            response = super().form_valid(form)
            
            # Audit log
            log_action(
                self.request, 'CREATE', self.object,
                object_name=f'Stock: {product.name}',
                description=f'Created stock record for "{product.name}" with {quantity} units',
                changes={
                    'Product': {'old': '—', 'new': str(product.name)},
                    'Quantity': {'old': '—', 'new': str(quantity)},
                    'Supplier': {'old': '—', 'new': str(supplier) if supplier else 'N/A'},
                    'Reorder Level': {'old': '—', 'new': str(reorder_level) if reorder_level else 'N/A'},
                }
            )
            
            messages.success(self.request, f"Stock record created for {product.name} with {quantity} units.")
            return response

class StockUpdateView(LoginRequiredMixin, InventoryUpdateMixin):
    model = Stock
    template_name = 'inventory/stock_form.html'
    form_class = StockForm
    success_url = reverse_lazy('stock_list')

class StockDeleteView(LoginRequiredMixin, InventoryDeleteMixin):
    model = Stock
    template_name = 'inventory/stock_confirm_delete.html'
    success_url = reverse_lazy('stock_list')

class InventoryPrintReportView(LoginRequiredMixin, TemplateView):
    """
    Generate printable inventory report
    Includes all stock levels, status, and reorder information
    """
    template_name = 'inventory/stock_print_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all stock with related product and supplier data
        stocks = Stock.objects.select_related('product', 'supplier').all()
        
        # Apply search filter if provided
        search_query = self.request.GET.get('search', '')
        if search_query:
            stocks = stocks.filter(
                Q(product__name__icontains=search_query) |
                Q(supplier__name__icontains=search_query)
            )
        
        # Apply stock status filter
        stock_status = self.request.GET.get('stock_status', '')
        if stock_status == 'no_stocks':
            stocks = stocks.filter(quantity=0)
        elif stock_status == 'critical':
            stocks = stocks.filter(quantity__lte=F('reorder_level'))
        elif stock_status == 'warning':
            stocks = stocks.filter(
                quantity__gt=F('reorder_level'),
                quantity__lte=F('reorder_level') + 15
            )
        elif stock_status == 'healthy':
            stocks = stocks.filter(quantity__gt=F('reorder_level') + 15)
        
        # Get sorting preference
        sort_by = self.request.GET.get('sort_by', 'product')
        if sort_by == 'quantity':
            stocks = stocks.order_by('quantity')
        elif sort_by == 'reorder_level':
            stocks = stocks.order_by('reorder_level')
        elif sort_by == 'supplier':
            stocks = stocks.order_by('supplier__name')
        else:  # Default to product name
            stocks = stocks.order_by('product__name')
        
        # Calculate summary statistics
        total_items = stocks.count()
        total_units = stocks.aggregate(total=Coalesce(Sum('quantity'), 0))['total']
        critical_count = stocks.filter(quantity__lte=F('reorder_level')).count()
        no_stock_count = stocks.filter(quantity=0).count()
        
        context['stocks'] = stocks
        context['total_items'] = total_items
        context['total_units'] = total_units
        context['critical_count'] = critical_count
        context['no_stock_count'] = no_stock_count
        context['search_query'] = search_query
        context['stock_status'] = stock_status
        context['sort_by'] = sort_by
        context['generated_date'] = datetime.now()
        
        return context
