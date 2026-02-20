from django.contrib.contenttypes.models import ContentType
from .models import AuditLog


def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_action(request, action, obj=None, object_name='', description='', changes=None):
    """
    Universal audit logging helper.
    
    Usage:
        log_action(request, 'CREATE', product, description='Created product "Widget"')
        log_action(request, 'UPDATE', stock, changes={'quantity': {'old': 10, 'new': 20}})
        log_action(request, 'DELETE', object_name='Product: Widget', description='Deleted product')
    """
    user = request.user if request.user.is_authenticated else None
    ip_address = get_client_ip(request)
    
    content_type = None
    object_id = ''
    
    if obj is not None:
        try:
            content_type = ContentType.objects.get_for_model(obj)
            object_id = str(obj.pk)
            if not object_name:
                object_name = str(obj)
        except Exception:
            pass
    
    AuditLog.objects.create(
        user=user,
        action=action,
        content_type=content_type,
        object_id=object_id,
        object_name=object_name,
        ip_address=ip_address,
        description=description,
        changes=changes,
    )


def get_model_changes(instance, form):
    """
    Compare form changed_data against the original instance to build a
    changes dict like {'field': {'old': ..., 'new': ...}}.
    
    Call BEFORE super().form_valid() to capture old values.
    """
    changes = {}
    if not hasattr(form, 'changed_data'):
        return changes
    
    for field_name in form.changed_data:
        old_value = None
        new_value = form.cleaned_data.get(field_name)
        
        if instance and instance.pk:
            try:
                old_value = getattr(instance, field_name, None)
                # Handle foreign keys
                field_obj = instance._meta.get_field(field_name)
                if field_obj.is_relation and old_value is not None:
                    old_value = str(old_value)
            except Exception:
                old_value = '—'
        
        # Convert to string for JSON serialization
        if hasattr(new_value, '__str__'):
            new_value = str(new_value)
        if hasattr(old_value, '__str__') and old_value is not None:
            old_value = str(old_value)
        
        # Skip unchanged or file fields that show the same path
        if str(old_value) == str(new_value):
            continue
        
        # Use verbose field label
        try:
            label = instance._meta.get_field(field_name).verbose_name.title()
        except Exception:
            label = field_name.replace('_', ' ').title()
        
        changes[label] = {
            'old': old_value if old_value not in (None, '', 'None') else '—',
            'new': new_value if new_value not in (None, '', 'None') else '—',
        }
    
    return changes
