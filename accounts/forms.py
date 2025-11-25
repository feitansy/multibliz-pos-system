from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    """
    Custom user registration form with additional fields.
    """
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)
    company_name = forms.CharField(max_length=100, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'company_name', 'address', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        """
        Override save to create regular users (not staff/admin).
        New users get the 'staff' role but NOT Django's is_staff permission.
        Only superusers/admins should have is_staff=True.
        """
        user = super().save(commit=False)
        user.is_staff = False  # Regular users should NOT have admin access
        user.role = 'staff'    # Default role is staff (not admin)
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom login form with styled widgets and error handling.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
    
    def clean(self):
        """
        Override clean to provide custom error messages.
        """
        cleaned_data = super().clean()
        if self.errors:
            # This will be automatically displayed in the template
            pass
        return cleaned_data
