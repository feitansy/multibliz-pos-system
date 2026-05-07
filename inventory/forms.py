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
        # Allow selecting any product with existing stock (for update) or products without stock (for create)
        if not self.instance.pk:
            # For create: show all products - we'll update existing stock or create new
            self.fields['product'].queryset = Product.objects.all().order_by('name')
        
        # Add empty option for supplier
        self.fields['supplier'].required = False
        self.fields['supplier'].empty_label = "Select a supplier (optional)"

    def clean_product(self):
        """
        Allow selecting products with existing stock when creating.
        The view (StockCreateView) handles updating existing stock.
        """
        product = self.cleaned_data.get('product')
        
        # Only validate uniqueness on update, not on create
        # On create, the view will check and update existing stock if needed
        if self.instance.pk:
            # This is an update - check if another stock record uses this product
            existing = Stock.objects.filter(product=product).exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('Stock with this Product already exists.')
        
        return product
    
    def validate_unique(self):
        """
        Skip unique validation for product field on create.
        The view handles merging with existing stock.
        """
        if not self.instance.pk:
            # Skip all unique validation on create
            pass
        else:
            # Run normal unique validation on update
            super().validate_unique()


class SupplierForm(forms.ModelForm):
    """Form for creating and updating suppliers"""
    
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'contact_email', 'contact_phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter supplier name',
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact person name',
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address',
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required
        self.fields['name'].required = True
        self.fields['contact_person'].required = True
        self.fields['contact_email'].required = True
        self.fields['contact_phone'].required = True
        self.fields['address'].required = True
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise forms.ValidationError('Company name is required.')
        return name.strip()
    
    def clean_contact_person(self):
        contact_person = self.cleaned_data.get('contact_person')
        if not contact_person or not contact_person.strip():
            raise forms.ValidationError('Contact person is required.')
        return contact_person.strip()
    
    def clean_contact_email(self):
        email = self.cleaned_data.get('contact_email')
        if not email or not email.strip():
            raise forms.ValidationError('Email address is required.')
        return email.strip()
    
    def clean_contact_phone(self):
        phone = self.cleaned_data.get('contact_phone')
        if not phone or not phone.strip():
            raise forms.ValidationError('Phone number is required.')
        return phone.strip()
    
    def clean_address(self):
        address = self.cleaned_data.get('address')
        if not address or not address.strip():
            raise forms.ValidationError('Address is required.')
        return address.strip()
