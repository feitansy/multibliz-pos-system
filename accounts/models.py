from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
import random

class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser with Role-Based Access Control (RBAC).
    
    Roles:
    - admin: Full administrative access (can delete records, manage users, etc.)
    - manager: Management access (can view and modify most records)
    - staff: Standard staff access (can create and view records, but cannot delete)
    - viewer: Read-only access (can only view records)
    """
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
        ('viewer', 'Viewer'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='staff',
        help_text='User role determines permission level for sensitive actions like deletion.'
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username
    
    def is_admin(self):
        """
        Check if user has admin privileges.
        Used for critical operations like deletion.
        """
        return self.role == 'admin' or self.is_superuser
    
    def is_manager(self):
        """
        Check if user has manager or higher privileges.
        """
        return self.role in ['admin', 'manager'] or self.is_superuser
    
    def is_staff_member(self):
        """
        Check if user has staff or higher privileges.
        """
        return self.role in ['admin', 'manager', 'staff'] or self.is_superuser
    
    def can_delete(self):
        """
        Permission check for deletion operations.
        Only admins and superusers can delete records.
        """
        return self.is_admin()


class PasswordResetOTP(models.Model):
    """
    Model to store OTP codes for password reset.
    Each OTP is valid for 10 minutes.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_otps')
    code = models.CharField(max_length=6, help_text='6-digit OTP code')
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Password Reset OTP'
        verbose_name_plural = 'Password Reset OTPs'
    
    def __str__(self):
        return f"OTP for {self.user.username} - {self.code}"
    
    def is_expired(self):
        """
        Check if OTP is expired (10 minutes validity).
        """
        expiration_time = self.created_at + timedelta(minutes=10)
        return timezone.now() > expiration_time
    
    def is_valid(self):
        """
        Check if OTP is valid (not used and not expired).
        """
        return not self.is_used and not self.is_expired()
    
    @staticmethod
    def generate_code():
        """
        Generate a random 6-digit code.
        """
        return str(random.randint(100000, 999999))
    
    @classmethod
    def create_for_user(cls, user):
        """
        Create a new OTP for a user and invalidate old ones.
        """
        # Mark all previous OTPs for this user as used
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Create new OTP
        code = cls.generate_code()
        otp = cls.objects.create(user=user, code=code)
        return otp
