from django.shortcuts import render
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

class StockCreateView(LoginRequiredMixin, InventoryCreateMixin):
    model = Stock
    template_name = 'inventory/stock_form.html'
    form_class = StockForm
    success_url = reverse_lazy('stock_list')

class StockUpdateView(LoginRequiredMixin, InventoryUpdateMixin):
    model = Stock
    template_name = 'inventory/stock_form.html'
    form_class = StockForm
    success_url = reverse_lazy('stock_list')

class StockDeleteView(LoginRequiredMixin, InventoryDeleteMixin):
    model = Stock
    template_name = 'inventory/stock_confirm_delete.html'
    success_url = reverse_lazy('stock_list')
