from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import AuditLog


def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log user login"""
    ip_address = get_client_ip(request)
    AuditLog.objects.create(
        user=user,
        action='LOGIN',
        object_name=f'{user.get_full_name() or user.username}',
        ip_address=ip_address,
        description=f'User {user.username} logged in'
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout"""
    ip_address = get_client_ip(request)
    AuditLog.objects.create(
        user=user,
        action='LOGOUT',
        object_name=f'{user.get_full_name() or user.username}',
        ip_address=ip_address,
        description=f'User {user.username} logged out'
    )
