from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
import json

User = get_user_model()


class AuditLog(models.Model):
    """Track all user actions across the system"""
    
    ACTION_CHOICES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
        ('VIEW', 'Viewed'),
        ('LOGIN', 'Logged In'),
        ('LOGOUT', 'Logged Out'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.CharField(max_length=255, blank=True)
    object_name = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    changes = models.JSONField(null=True, blank=True, help_text="Track what changed")
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.object_name} ({self.timestamp})"
    
    @property
    def get_action_display_badge(self):
        """Return badge color based on action"""
        colors = {
            'CREATE': '#10b981',
            'UPDATE': '#3b82f6',
            'DELETE': '#ef4444',
            'VIEW': '#6b7280',
            'LOGIN': '#8b5cf6',
            'LOGOUT': '#f97316',
        }
        return colors.get(self.action, '#6b7280')
    
    @property
    def changes_display(self):
        """Format changes for display"""
        if self.changes and isinstance(self.changes, dict):
            changes_text = []
            for key, value in self.changes.items():
                if isinstance(value, dict):
                    old = value.get('old', '')
                    new = value.get('new', '')
                    changes_text.append(f"{key}: {old} → {new}")
                else:
                    changes_text.append(f"{key}: {value}")
            return "; ".join(changes_text)
        return "—"
