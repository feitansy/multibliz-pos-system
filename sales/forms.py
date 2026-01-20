from django import forms
from .models import Product, Sale, Return
from inventory.models import Supplier


class ProductForm(forms.ModelForm):
    """Form for creating and updating products"""
    
    # Add supplier field (stored on Stock model, not Product)
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        required=False,
        empty_label="Select a supplier (optional)",
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
        })
    )
    
    class Meta:
        model = Product
        fields = ['name', 'label', 'description', 'price', 'category', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name',
                'required': True,
            }),
            'label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Receipt label/SKU (optional)',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product description (optional)',
                'rows': 3,
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter price',
                'step': '0.01',
                'min': '0',
                'required': True,
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category (optional)',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
        }


class SaleForm(forms.ModelForm):
    """Form for creating and updating sales"""
    
    class Meta:
        model = Sale
        fields = ['product', 'quantity', 'total_price', 'customer_name']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-control form-select',
                'required': True,
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Enter quantity',
                'required': True,
            }),
            'total_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Enter total price',
                'required': True,
            }),
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter customer name (optional)',
            }),
        }


class ReturnForm(forms.ModelForm):
    """Form for creating and updating returns"""
    
    # Explicitly define sale field with ordered queryset
    sale = forms.ModelChoiceField(
        queryset=Sale.objects.all().order_by('-id'),
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
            'required': True,
        }),
        label='Sale',
        help_text='Select the sale to return'
    )
    
    class Meta:
        model = Return
        fields = ['sale', 'quantity_returned', 'reason', 'reason_details', 'refund_amount', 'status']
        widgets = {
            'sale': forms.Select(attrs={
                'class': 'form-control form-select',
                'required': True,
            }),
            'quantity_returned': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Enter quantity to return',
                'required': True,
            }),
            'reason': forms.Select(attrs={
                'class': 'form-control form-select',
                'required': True,
            }),
            'reason_details': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter additional details (optional)',
                'rows': 3,
            }),
            'refund_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Enter refund amount',
                'required': True,
            }),
            'status': forms.Select(attrs={
                'class': 'form-control form-select',
            }),
        }
    
    def clean_sale(self):
        """Validate that the sale doesn't already have an active return"""
        sale = self.cleaned_data.get('sale')
        
        if sale:
            # Check if there's already a pending, approved, or completed return for this sale
            active_returns = Return.objects.filter(
                sale=sale,
                status__in=['pending', 'approved', 'completed']
            ).exists()
            
            if active_returns:
                raise forms.ValidationError(
                    f"A return request already exists for Sale #{sale.id}. "
                    f"Only one active return per sale is allowed. "
                    f"Please check the return status or contact an administrator."
                )
        
        return sale
