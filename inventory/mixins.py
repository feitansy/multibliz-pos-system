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
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(product__name__icontains=search_query) |
                Q(supplier__name__icontains=search_query) |
                Q(id__icontains=search_query)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
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
