from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.forms import SetPasswordForm
from .forms import CustomUserCreationForm, CustomAuthenticationForm
import threading

class SignUpView(CreateView):
    """
    View for user registration.
    """
    form_class = CustomUserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Account created successfully! Please log in.')
        return super().form_valid(form)

def login_view(request):
    """
    Custom login view with error handling.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            # Display error message for invalid credentials
            if form.non_field_errors():
                messages.error(request, 'Invalid username or password. Please try again.')
            else:
                messages.error(request, 'Please check your username and password.')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    """
    Custom logout view.
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def account_settings(request):
    """
    User account settings page - view and edit profile.
    """
    from django.contrib.auth import get_user_model
    import json
    
    user = request.user
    
    # Get users data for admin users
    users_json = '[]'
    if user.is_staff:
        User = get_user_model()
        users = User.objects.all().order_by('-date_joined')
        
        users_data = []
        for u in users:
            initials = ''
            if u.first_name and u.last_name:
                initials = (u.first_name[0] + u.last_name[0]).upper()
            else:
                initials = u.username[:2].upper()
            
            users_data.append({
                'id': u.id,
                'username': u.username,
                'full_name': u.get_full_name() or u.username,
                'initials': initials,
                'email': u.email,
                'is_staff': u.is_staff,
                'date_joined': u.date_joined.isoformat(),
            })
        
        users_json = json.dumps(users_data)
    
    context = {
        'user': user,
        'role_display': user.get_role_display(),
        'joined_date': user.date_joined,
        'users_json': users_json,
    }
    return render(request, 'accounts/settings.html', context)


@login_required
def change_password(request):
    """
    Change password view with validation.
    """
    if request.method == 'POST':
        form = SetPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('account_settings')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = SetPasswordForm(user=request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def security_dashboard(request):
    """
    Security dashboard showing account security status and recommendations.
    """
    from django.utils import timezone
    from datetime import timedelta
    
    user = request.user
    
    # Calculate security score (0-100)
    security_score = 0
    recommendations = []
    
    # Password age check (worth 30 points)
    if user.date_joined:
        days_since_join = (timezone.now() - user.date_joined).days
        if days_since_join > 90:
            recommendations.append({
                'type': 'warning',
                'title': 'Password Change Recommended',
                'message': 'Consider changing your password every 90 days for better security.'
            })
        else:
            security_score += 30
    
    # Email verification (worth 20 points)
    if user.email:
        security_score += 20
    else:
        recommendations.append({
            'type': 'danger',
            'title': 'Add Email Address',
            'message': 'Having a verified email helps protect your account.'
        })
    
    # Profile completeness (worth 30 points)
    profile_fields = [user.get_full_name(), user.phone, user.address, user.company_name]
    filled_fields = sum(1 for field in profile_fields if field)
    security_score += (filled_fields / len(profile_fields)) * 30
    
    if filled_fields < len(profile_fields):
        recommendations.append({
            'type': 'info',
            'title': 'Complete Your Profile',
            'message': f'You have {len(profile_fields) - filled_fields} profile fields empty. Complete your profile for better security.'
        })
    
    # Active sessions (worth 20 points)
    security_score += 20  # Placeholder for future session tracking
    
    # Recent activity
    last_login = user.last_login
    recent_activity = []
    if last_login:
        recent_activity.append({
            'action': 'Last Login',
            'date': last_login,
            'icon': 'sign-in-alt'
        })
    
    if user.date_joined:
        recent_activity.append({
            'action': 'Account Created',
            'date': user.date_joined,
            'icon': 'user-check'
        })
    
    context = {
        'user': user,
        'security_score': int(security_score),
        'recommendations': recommendations,
        'recent_activity': recent_activity,
    }
    
    return render(request, 'accounts/security_dashboard.html', context)


@login_required
def edit_profile(request):
    """
    Allow users to edit their profile information.
    """
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.address = request.POST.get('address', user.address)
        user.company_name = request.POST.get('company_name', user.company_name)
        
        try:
            user.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('account_settings')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    return render(request, 'accounts/edit_profile.html', {'user': request.user})


@login_required
def user_management(request):
    """
    Admin user management page - view and delete users.
    Returns JSON data for AJAX requests.
    """
    from django.contrib.auth import get_user_model
    import json
    
    # Check if user is admin
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    User = get_user_model()
    users = User.objects.all().order_by('-date_joined')
    
    # Build users JSON data
    users_data = []
    for user in users:
        initials = ''
        if user.first_name and user.last_name:
            initials = (user.first_name[0] + user.last_name[0]).upper()
        else:
            initials = user.username[:2].upper()
        
        users_data.append({
            'id': user.id,
            'username': user.username,
            'full_name': user.get_full_name() or user.username,
            'initials': initials,
            'email': user.email,
            'is_staff': user.is_staff,
            'date_joined': user.date_joined.isoformat(),
        })
    
    # If request is for JSON (via AJAX), return JSON
    if request.headers.get('Accept') == 'application/json' or request.GET.get('format') == 'json':
        return JsonResponse(users_data, safe=False)
    
    # Otherwise render settings template with users data embedded
    context = {
        'users': users,
        'user_count': users.count(),
        'users_json': json.dumps(users_data),
    }
    
    return render(request, 'accounts/settings.html', context)


@login_required
def update_user_role(request, user_id):
    """
    Update a user's role (admin only).
    """
    from django.contrib.auth import get_user_model
    
    # Check if user is admin
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    User = get_user_model()
    
    try:
        user_to_update = User.objects.get(id=user_id)
        
        # Prevent admin from changing their own role
        if user_to_update.id == request.user.id:
            return JsonResponse({'success': False, 'error': 'You cannot change your own role'})
        
        # Get new role from request
        new_role = request.POST.get('role', 'staff')
        
        # Prevent making all admins into staff if this is the last admin
        if user_to_update.is_staff and new_role == 'staff':
            admin_count = User.objects.filter(is_staff=True).count()
            if admin_count <= 1:
                return JsonResponse({'success': False, 'error': 'Cannot demote the last admin user'})
        
        # Update role
        if new_role == 'admin':
            user_to_update.is_staff = True
        else:
            user_to_update.is_staff = False
        
        user_to_update.save()
        
        messages.success(request, f'User "{user_to_update.username}" role updated to {new_role.upper()}')
        return JsonResponse({
            'success': True,
            'message': f'User role updated to {new_role.upper()}',
            'new_role': new_role,
            'is_staff': user_to_update.is_staff
        })
    
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================
# OTP-Based Password Reset Views
# ============================================

def forgot_password_request(request):
    """
    Step 1: User enters username/email to request OTP.
    Generates 6-digit code and sends via Email and SMS.
    """
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email', '').strip()
        
        if not username_or_email:
            messages.error(request, 'Please enter your username or email.')
            return render(request, 'accounts/forgot_password_request.html')
        
        # Try to find user by username or email
        from django.contrib.auth import get_user_model
        from .models import PasswordResetOTP
        
        User = get_user_model()
        user = None
        
        try:
            # Try username first (use filter().first() to handle duplicates)
            user = User.objects.filter(username=username_or_email).first()
            if not user:
                # Try email
                user = User.objects.filter(email=username_or_email).first()
            
            if not user:
                # Don't reveal if user exists or not for security
                messages.info(request, 'If an account exists with that username/email, an OTP code has been sent.')
                return render(request, 'accounts/forgot_password_request.html')
        except Exception as e:
            # Log error but don't reveal details to user
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error in password reset: {str(e)}')
            messages.error(request, 'An error occurred. Please try again.')
            return render(request, 'accounts/forgot_password_request.html')
        
        # Generate OTP
        otp = PasswordResetOTP.create_for_user(user)
        
        # Send OTP via Email (asynchronously to prevent timeout on Render)
        def send_otp_email():
            try:
                from django.conf import settings
                
                subject = 'Password Reset OTP - Multibliz POS'
                message = f'''
Hello {user.username},

You requested to reset your password. Your OTP code is:

{otp.code}

This code is valid for 10 minutes.

If you did not request this, please ignore this email.

Best regards,
Multibliz POS Team
                '''
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True,  # Changed to True for async - don't block request
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Failed to send OTP email: {str(e)}')
        
        # Send email in background thread
        import threading
        email_thread = threading.Thread(target=send_otp_email, daemon=True)
        email_thread.start()
        
        # Send OTP via SMS (Twilio) - Optional (asynchronously)
        def send_otp_sms():
            if user.phone:
                try:
                    from django.conf import settings
                    from twilio.rest import Client
                    
                    # Check if Twilio credentials are configured
                    if (hasattr(settings, 'TWILIO_ACCOUNT_SID') and 
                        hasattr(settings, 'TWILIO_AUTH_TOKEN') and 
                        hasattr(settings, 'TWILIO_PHONE_NUMBER') and
                        settings.TWILIO_ACCOUNT_SID and 
                        settings.TWILIO_AUTH_TOKEN and
                        settings.TWILIO_PHONE_NUMBER and
                        not settings.TWILIO_ACCOUNT_SID.startswith('your_') and
                        not settings.TWILIO_AUTH_TOKEN.startswith('your_')):
                        
                        # Initialize Twilio client
                        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                        
                        sms_message = f'Your Multibliz POS password reset OTP is: {otp.code}. Valid for 10 minutes.'
                        
                        message = client.messages.create(
                            body=sms_message,
                            from_=settings.TWILIO_PHONE_NUMBER,
                            to=user.phone
                        )
                    else:
                        # Twilio not configured - silently skip SMS
                        pass
                    
                except ImportError:
                    # Twilio package not installed - silently skip SMS
                    pass
                except Exception as e:
                    # SMS failed but don't block the password reset - email is primary
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f'SMS sending failed: {str(e)}')
        
        # Send SMS in background thread
        sms_thread = threading.Thread(target=send_otp_sms, daemon=True)
        sms_thread.start()
        
        # Store user_id in session for verification step
        request.session['reset_user_id'] = user.id
        request.session['otp_sent_time'] = str(otp.created_at)
        
        messages.success(request, 'OTP code has been sent to your email.')
        return redirect('verify_otp')
    
    return render(request, 'accounts/forgot_password_request.html')


def verify_otp(request):
    """
    Step 2: User enters the 6-digit OTP code to verify.
    Validates code and checks expiration.
    """
    # Check if user_id exists in session
    user_id = request.session.get('reset_user_id')
    
    if not user_id:
        messages.error(request, 'Session expired. Please request a new OTP.')
        return redirect('forgot_password_request')
    
    if request.method == 'POST':
        entered_code = request.POST.get('otp_code', '').strip()
        
        if not entered_code:
            messages.error(request, 'Please enter the OTP code.')
            return render(request, 'accounts/verify_otp.html')
        
        # Get user and verify OTP
        from django.contrib.auth import get_user_model
        from .models import PasswordResetOTP
        
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
            
            # Get the latest OTP for this user
            try:
                otp = PasswordResetOTP.objects.filter(
                    user=user,
                    code=entered_code,
                    is_used=False
                ).latest('created_at')
                
                # Check if OTP is valid
                if otp.is_valid():
                    # Mark OTP as used
                    otp.is_used = True
                    otp.save()
                    
                    # Store verification flag in session
                    request.session['otp_verified'] = True
                    
                    messages.success(request, 'OTP verified! Please set your new password.')
                    return redirect('reset_password')
                else:
                    if otp.is_expired():
                        messages.error(request, 'OTP code has expired. Please request a new one.')
                    else:
                        messages.error(request, 'OTP code has already been used.')
                    
                    return render(request, 'accounts/verify_otp.html')
                    
            except PasswordResetOTP.DoesNotExist:
                messages.error(request, 'Invalid OTP code. Please try again.')
                return render(request, 'accounts/verify_otp.html')
                
        except User.DoesNotExist:
            messages.error(request, 'Session error. Please start over.')
            return redirect('forgot_password_request')
    
    return render(request, 'accounts/verify_otp.html')


def reset_password(request):
    """
    Step 3: User sets a new password after OTP verification.
    """
    # Check if OTP was verified
    if not request.session.get('otp_verified'):
        messages.error(request, 'Please verify your OTP first.')
        return redirect('verify_otp')
    
    user_id = request.session.get('reset_user_id')
    
    if not user_id:
        messages.error(request, 'Session expired. Please start over.')
        return redirect('forgot_password_request')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        if not new_password or not confirm_password:
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'accounts/reset_password.html')
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/reset_password.html')
        
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'accounts/reset_password.html')
        
        # Get user and update password
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()
            
            # Clear session data
            request.session.pop('reset_user_id', None)
            request.session.pop('otp_verified', None)
            request.session.pop('otp_sent_time', None)
            
            messages.success(request, 'Your password has been reset successfully! Please log in.')
            return redirect('login')
            
        except User.DoesNotExist:
            messages.error(request, 'User not found. Please start over.')
            return redirect('forgot_password_request')
    
    return render(request, 'accounts/reset_password.html')


@login_required
def delete_user(request, user_id):
    """
    Delete a user (admin only).
    """
    from django.contrib.auth import get_user_model
    
    # Check if user is admin
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    User = get_user_model()
    
    try:
        user_to_delete = User.objects.get(id=user_id)
        
        # Prevent admin from deleting themselves
        if user_to_delete.id == request.user.id:
            return JsonResponse({'success': False, 'error': 'You cannot delete your own account'})
        
        # Prevent deleting the last admin
        if user_to_delete.is_staff:
            admin_count = User.objects.filter(is_staff=True).count()
            if admin_count <= 1:
                return JsonResponse({'success': False, 'error': 'Cannot delete the last admin user'})
        
        username = user_to_delete.username
        user_to_delete.delete()
        
        messages.success(request, f'User "{username}" has been deleted successfully.')
        return JsonResponse({'success': True, 'message': f'User "{username}" deleted'})
    
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)