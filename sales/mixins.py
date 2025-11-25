from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from inventory.models import Stock

class ProductMixin:
    model = None  # To be set in subclasses
    template_name = None
    success_url = None

class ProductListMixin(ProductMixin, ListView):
    context_object_name = 'products'
    paginate_by = 25

class ProductDetailMixin(ProductMixin, DetailView):
    pass

class ProductCreateMixin(ProductMixin, CreateView):
    def form_valid(self, form):
        # Save the product first
        response = super().form_valid(form)
        
        # Update the auto-created stock record with the supplier
        supplier = form.cleaned_data.get('supplier')
        if supplier:
            try:
                stock = Stock.objects.get(product=self.object)
                stock.supplier = supplier
                stock.save()
            except Stock.DoesNotExist:
                # Stock should be auto-created by signal, but just in case
                Stock.objects.create(product=self.object, supplier=supplier)
        
        messages.success(self.request, f"{self.model._meta.verbose_name} created successfully.")
        return response

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
