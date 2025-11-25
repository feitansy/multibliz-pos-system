from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

class ProductMixin:
    model = None  # To be set in subclasses
    template_name = None
    success_url = None

class ProductListMixin(ProductMixin, ListView):
    context_object_name = 'products'

class ProductDetailMixin(ProductMixin, DetailView):
    pass

class ProductCreateMixin(ProductMixin, CreateView):
    def form_valid(self, form):
        messages.success(self.request, f"{self.model._meta.verbose_name} created successfully.")
        return super().form_valid(form)

class ProductUpdateMixin(ProductMixin, UpdateView):
    def form_valid(self, form):
        messages.success(self.request, f"{self.model._meta.verbose_name} updated successfully.")
        return super().form_valid(form)

class ProductDeleteMixin(ProductMixin, DeleteView):
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, f"{self.model._meta.verbose_name} deleted successfully.")
        return super().delete(request, *args, **kwargs)
