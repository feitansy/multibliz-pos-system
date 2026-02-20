from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import AuditLog


def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_browser_info(request):
    """Extract browser/device info from User-Agent"""
    ua = request.META.get('HTTP_USER_AGENT', 'Unknown')
    
    # Simple browser detection
    browser = 'Unknown'
    if 'Chrome' in ua and 'Edg' not in ua:
        browser = 'Chrome'
    elif 'Firefox' in ua:
        browser = 'Firefox'
    elif 'Safari' in ua and 'Chrome' not in ua:
        browser = 'Safari'
    elif 'Edg' in ua:
        browser = 'Microsoft Edge'
    elif 'Opera' in ua or 'OPR' in ua:
        browser = 'Opera'
    
    # Simple OS detection
    os_name = 'Unknown'
    if 'Windows' in ua:
        os_name = 'Windows'
    elif 'Mac OS' in ua:
        os_name = 'macOS'
    elif 'Linux' in ua:
        os_name = 'Linux'
    elif 'Android' in ua:
        os_name = 'Android'
    elif 'iPhone' in ua or 'iPad' in ua:
        os_name = 'iOS'
    
    return browser, os_name


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log user login with browser and device info"""
    ip_address = get_client_ip(request)
    browser, os_name = get_browser_info(request)
    
    AuditLog.objects.create(
        user=user,
        action='LOGIN',
        object_name=f'{user.get_full_name() or user.username}',
        ip_address=ip_address,
        description=f'User "{user.username}" logged in from {browser} on {os_name} (IP: {ip_address})',
        changes={
            'Browser': {'old': '—', 'new': browser},
            'Operating System': {'old': '—', 'new': os_name},
        }
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout with session duration"""
    ip_address = get_client_ip(request)
    browser, os_name = get_browser_info(request)
    
    # Calculate approximate session duration
    duration_text = ''
    if user and user.last_login:
        from django.utils import timezone
        duration = timezone.now() - user.last_login
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        if hours > 0:
            duration_text = f' (session ~{hours}h {minutes}m)'
        else:
            duration_text = f' (session ~{minutes}m)'
    
    AuditLog.objects.create(
        user=user,
        action='LOGOUT',
        object_name=f'{user.get_full_name() or user.username}',
        ip_address=ip_address,
        description=f'User "{user.username}" logged out{duration_text}',
    )
