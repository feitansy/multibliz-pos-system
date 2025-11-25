from django import forms
from .models import Stock, Supplier
from sales.models import Product


class StockForm(forms.ModelForm):
    """Form for creating and updating stock records"""
    
    class Meta:
        model = Stock
        fields = ['product', 'supplier', 'quantity', 'reorder_level']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-control form-select',
                'required': True,
            }),
            'supplier': forms.Select(attrs={
                'class': 'form-control form-select',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Enter quantity',
            }),
            'reorder_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Enter reorder level',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show products that don't have stock records yet (for create)
        if not self.instance.pk:
            existing_stock_products = Stock.objects.values_list('product_id', flat=True)
            self.fields['product'].queryset = Product.objects.exclude(id__in=existing_stock_products)
        
        # Add empty option for supplier
        self.fields['supplier'].required = False
        self.fields['supplier'].empty_label = "Select a supplier (optional)"


class SupplierForm(forms.ModelForm):
    """Form for creating and updating suppliers"""
    
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'contact_email', 'contact_phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter supplier name',
                'required': True,
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact person name',
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address',
                'required': True,
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter address',
                'rows': 3,
            }),
        }
