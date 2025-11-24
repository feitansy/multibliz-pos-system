"""
Role-Based Access Control (RBAC) Permissions Module

This module provides permission checking utilities and mixins to enforce
role-based access control throughout the application, with special emphasis
on protecting sensitive operations like deletion.
"""

from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.contrib import messages


class AdminRequiredMixin(UserPassesTestMixin):
    """
    Mixin to restrict view access to admin users only.
    
    Usage:
        class SensitiveDeleteView(AdminRequiredMixin, DeleteView):
            model = MyModel
            
    This mixin ensures that only users with admin role can access the view.
    Raises 403 Forbidden if user lacks admin privileges.
    """
    
    def test_func(self):
        """
        Test function to check if user has admin role.
        Returns True if user is admin, False otherwise.
        """
        # Check if user is authenticated
        if not self.request.user.is_authenticated:
            return False
        
        # Check if user has admin role or is superuser
        has_admin = self.request.user.is_admin()
        return has_admin
    
    def handle_no_permission(self):
        """
        Handle permission denied - log and show error message.
        """
        messages.error(
            self.request,
            '❌ Permission Denied: Only administrators can perform this action.'
        )
        # Raise 403 Forbidden
        raise PermissionDenied("Only administrators can perform this action.")


class ManagerRequiredMixin(UserPassesTestMixin):
    """
    Mixin to restrict view access to manager users and above (includes admins).
    
    Usage:
        class ReportView(ManagerRequiredMixin, ListView):
            model = Report
    """
    
    def test_func(self):
        """
        Test function to check if user has manager role or higher.
        """
        if not self.request.user.is_authenticated:
            return False
        
        return self.request.user.is_manager()
    
    def handle_no_permission(self):
        """Handle permission denied."""
        messages.error(
            self.request,
            '❌ Permission Denied: Manager access required.'
        )
        raise PermissionDenied("Manager or higher privileges required.")


class StaffRequiredMixin(UserPassesTestMixin):
    """
    Mixin to restrict view access to staff users and above.
    """
    
    def test_func(self):
        """Test function to check if user has staff role or higher."""
        if not self.request.user.is_authenticated:
            return False
        
        return self.request.user.is_staff_member()
    
    def handle_no_permission(self):
        """Handle permission denied."""
        messages.error(
            self.request,
            '❌ Permission Denied: Staff access or higher required.'
        )
        raise PermissionDenied("Staff or higher privileges required.")


class CanDeleteMixin:
    """
    Mixin to protect delete operations.
    
    This mixin should be used with DeleteView to ensure only authorized
    users (admins) can delete records. It provides two levels of protection:
    
    1. Dispatch-level: Checks permission before processing the request
    2. Delete-level: Double-checks before actual deletion
    """
    
    def dispatch(self, request, *args, **kwargs):
        """
        Check permission at dispatch level before any processing.
        
        This happens early in the request cycle, preventing unnecessary
        processing of unauthorized requests.
        """
        # Ensure user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, 'Authentication required.')
            raise PermissionDenied("User must be authenticated.")
        
        # Check if user can delete
        if not request.user.can_delete():
            messages.error(
                request,
                f'❌ Permission Denied: Only administrators can delete records. '
                f'Your role: {request.user.get_role_display()}'
            )
            raise PermissionDenied(
                f"Only administrators can delete records. Your current role is: "
                f"{request.user.get_role_display()}"
            )
        
        # Permission granted, continue with request processing
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        """
        Secondary permission check before actual deletion.
        
        This acts as a safety mechanism to prevent any deletion
        even if dispatch was somehow bypassed.
        """
        # Double-check permission before deletion
        if not request.user.can_delete():
            messages.error(request, 'Deletion not permitted.')
            raise PermissionDenied("User does not have permission to delete.")
        
        # Log deletion for audit purposes
        object_to_delete = self.get_object()
        messages.success(
            request,
            f"✓ {object_to_delete.__class__.__name__} deleted successfully by {request.user.username}."
        )
        
        # Proceed with deletion
        return super().delete(request, *args, **kwargs)


def check_can_delete_permission(user):
    """
    Utility function to check if a user can delete records.
    
    Args:
        user: Django User object
        
    Returns:
        bool: True if user can delete, False otherwise
    """
    if not user.is_authenticated:
        return False
    
    return user.can_delete()


def check_admin_permission(user):
    """
    Utility function to check if a user has admin privileges.
    
    Args:
        user: Django User object
        
    Returns:
        bool: True if user is admin, False otherwise
    """
    if not user.is_authenticated:
        return False
    
    return user.is_admin()
