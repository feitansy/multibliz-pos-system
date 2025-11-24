from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'object_name', 'ip_address')
    list_filter = ('action', 'timestamp', 'user')
    search_fields = ('object_name', 'user__username', 'ip_address')
    readonly_fields = ('user', 'action', 'content_type', 'object_id', 'object_name', 'timestamp', 'ip_address', 'changes', 'description')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
