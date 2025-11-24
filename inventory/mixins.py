from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages

class InventoryMixin:
    model = None
    template_name = None
    success_url = None

class InventoryListMixin(InventoryMixin, ListView):
    context_object_name = 'items'

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
