from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db.models import Q
from .models import AuditLog


def is_admin(user):
    """Check if user is admin"""
    return user.is_staff and user.is_superuser


@login_required
@user_passes_test(is_admin)
def audit_trail_view(request):
    """Display audit trail for admin users only"""
    
    # Get filter parameters
    user_filter = request.GET.get('user', '').strip()
    action_filter = request.GET.get('action', '').strip()
    search = request.GET.get('search', '').strip()
    
    # Build query
    logs = AuditLog.objects.all()
    
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)
    
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    if search:
        logs = logs.filter(
            Q(object_name__icontains=search) |
            Q(description__icontains=search) |
            Q(user__username__icontains=search)
        )
    
    # Get distinct actions for filter dropdown
    actions = AuditLog.objects.values_list('action', flat=True).distinct()
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'logs': page_obj,
        'actions': actions,
        'user_filter': user_filter,
        'action_filter': action_filter,
        'search': search,
        'total_logs': paginator.count,
    }
    
    return render(request, 'audit/audit_trail.html', context)
