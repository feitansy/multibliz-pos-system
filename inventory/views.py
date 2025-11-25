from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Supplier, Stock
from .forms import StockForm, SupplierForm
from .mixins import InventoryListMixin, InventoryDetailMixin, InventoryCreateMixin, InventoryUpdateMixin, InventoryDeleteMixin

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
            # Update existing stock - ADD the new quantity to existing
            existing_stock.quantity += quantity
            if supplier:
                existing_stock.supplier = supplier
            if reorder_level:
                existing_stock.reorder_level = reorder_level
            existing_stock.save()
            messages.success(self.request, f"Added {quantity} units to {product.name}. New total: {existing_stock.quantity} units.")
            return redirect(self.success_url)
        except Stock.DoesNotExist:
            # Create new stock record
            messages.success(self.request, f"Stock record created for {product.name} with {quantity} units.")
            return super().form_valid(form)

class StockUpdateView(LoginRequiredMixin, InventoryUpdateMixin):
    model = Stock
    template_name = 'inventory/stock_form.html'
    form_class = StockForm
    success_url = reverse_lazy('stock_list')

class StockDeleteView(LoginRequiredMixin, InventoryDeleteMixin):
    model = Stock
    template_name = 'inventory/stock_confirm_delete.html'
    success_url = reverse_lazy('stock_list')
