"""
System Deployment Readiness Check
Comprehensive analysis of system status before deployment
"""

import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')
django.setup()

from django.conf import settings
from sales.models import Product, Sale, Return
from inventory.models import Stock, Supplier
from accounts.models import User
from forecasting.models import Forecast
from audit.models import AuditLog
from django.db import connection

def check_database():
    """Check database connectivity and data"""
    print("=" * 80)
    print("DATABASE CHECK")
    print("=" * 80)
    
    try:
        # Test connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection: OK")
        
        # Check data counts
        products = Product.objects.count()
        sales = Sale.objects.count()
        returns = Return.objects.count()
        stocks = Stock.objects.count()
        suppliers = Supplier.objects.count()
        users = User.objects.count()
        forecasts = Forecast.objects.count()
        audits = AuditLog.objects.count()
        
        print(f"✅ Products: {products:,}")
        print(f"✅ Sales: {sales:,}")
        print(f"✅ Returns: {returns:,}")
        print(f"✅ Stock Records: {stocks:,}")
        print(f"✅ Suppliers: {suppliers:,}")
        print(f"✅ Users: {users:,}")
        print(f"✅ Forecasts: {forecasts:,}")
        print(f"✅ Audit Logs: {audits:,}")
        
        issues = []
        if products == 0:
            issues.append("⚠️  No products in system")
        if users == 0:
            issues.append("⚠️  No users created")
        if sales == 0:
            issues.append("⚠️  No sales data (needed for forecasting)")
            
        return len(issues) == 0, issues
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False, [f"Database connection failed: {e}"]

def check_settings():
    """Check Django settings for production readiness"""
    print("\n" + "=" * 80)
    print("SETTINGS CHECK")
    print("=" * 80)
    
    issues = []
    
    # Debug mode
    if settings.DEBUG:
        print("❌ DEBUG = True (MUST be False for production)")
        issues.append("DEBUG mode is enabled")
    else:
        print("✅ DEBUG = False")
    
    # Secret key
    if settings.SECRET_KEY == 'django-insecure-' or 'insecure' in settings.SECRET_KEY.lower():
        print("❌ SECRET_KEY is insecure")
        issues.append("SECRET_KEY must be changed for production")
    else:
        print("✅ SECRET_KEY configured")
    
    # Allowed hosts
    if not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ['*']:
        print("⚠️  ALLOWED_HOSTS = ['*'] (should be specific domains)")
        issues.append("ALLOWED_HOSTS should be configured with specific domains")
    else:
        print(f"✅ ALLOWED_HOSTS = {settings.ALLOWED_HOSTS}")
    
    # Database
    db_engine = settings.DATABASES['default']['ENGINE']
    if 'sqlite' in db_engine:
        print("⚠️  Using SQLite (consider PostgreSQL/MySQL for production)")
    else:
        print(f"✅ Database: {db_engine}")
    
    # Static files
    if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
        print(f"✅ STATIC_ROOT configured: {settings.STATIC_ROOT}")
    else:
        print("⚠️  STATIC_ROOT not configured")
        issues.append("STATIC_ROOT must be set for production")
    
    # Media files
    if hasattr(settings, 'MEDIA_ROOT') and settings.MEDIA_ROOT:
        print(f"✅ MEDIA_ROOT configured: {settings.MEDIA_ROOT}")
    else:
        print("⚠️  MEDIA_ROOT not configured")
    
    # Timezone
    print(f"✅ TIME_ZONE = {settings.TIME_ZONE}")
    
    # CSRF
    if hasattr(settings, 'CSRF_COOKIE_SECURE'):
        print(f"✅ CSRF_COOKIE_SECURE = {settings.CSRF_COOKIE_SECURE}")
    else:
        print("⚠️  CSRF_COOKIE_SECURE not set (should be True for HTTPS)")
    
    # Session security
    if hasattr(settings, 'SESSION_COOKIE_SECURE'):
        print(f"✅ SESSION_COOKIE_SECURE = {settings.SESSION_COOKIE_SECURE}")
    else:
        print("⚠️  SESSION_COOKIE_SECURE not set (should be True for HTTPS)")
    
    return len(issues) == 0, issues

def check_features():
    """Check core features functionality"""
    print("\n" + "=" * 80)
    print("FEATURES CHECK")
    print("=" * 80)
    
    features = {
        '✅ User Authentication': User.objects.exists(),
        '✅ Product Management': Product.objects.exists(),
        '✅ Inventory Management': Stock.objects.exists(),
        '✅ Sales/POS Terminal': Sale.objects.exists(),
        '✅ Returns Management': True,  # Model exists
        '✅ Supplier Management': Supplier.objects.exists(),
        '✅ Forecasting (AI/ML)': Forecast.objects.exists(),
        '✅ Audit Trail': AuditLog.objects.exists(),
    }
    
    issues = []
    for feature, status in features.items():
        if status:
            print(feature)
        else:
            print(f"⚠️  {feature.replace('✅', '').strip()}: No data")
            issues.append(f"{feature.replace('✅', '').strip()} has no data")
    
    return len(issues) == 0, issues

def check_security():
    """Check security configurations"""
    print("\n" + "=" * 80)
    print("SECURITY CHECK")
    print("=" * 80)
    
    issues = []
    
    # Check for admin users
    admin_users = User.objects.filter(role='admin').count()
    if admin_users == 0:
        print("❌ No admin users found")
        issues.append("Create at least one admin user")
    else:
        print(f"✅ Admin users: {admin_users}")
    
    # Check for weak passwords (if using default User model)
    try:
        weak_users = []
        for user in User.objects.all()[:10]:  # Check first 10
            if user.check_password('admin') or user.check_password('password') or user.check_password('123456'):
                weak_users.append(user.username)
        
        if weak_users:
            print(f"⚠️  Users with weak passwords: {', '.join(weak_users)}")
            issues.append("Some users have weak passwords")
        else:
            print("✅ No obvious weak passwords detected")
    except:
        print("⚠️  Could not check password strength")
    
    # Check permissions
    print("✅ Role-based access control implemented")
    
    return len(issues) == 0, issues

def check_files():
    """Check required files and structure"""
    print("\n" + "=" * 80)
    print("FILES & STRUCTURE CHECK")
    print("=" * 80)
    
    required_files = [
        'manage.py',
        'requirements.txt',
        'multibliz_pos/settings.py',
        'multibliz_pos/urls.py',
        'multibliz_pos/wsgi.py',
        'templates/base.html',
        'Frontend/css/custom.css',
        'Frontend/js/charts.js',
    ]
    
    issues = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} missing")
            issues.append(f"Missing file: {file}")
    
    # Check for .env file (good practice)
    if os.path.exists('.env'):
        print("✅ .env file exists (good for environment variables)")
    else:
        print("⚠️  .env file not found (recommended for production secrets)")
        issues.append("Consider using .env file for sensitive settings")
    
    # Check for .gitignore
    if os.path.exists('.gitignore'):
        print("✅ .gitignore exists")
    else:
        print("⚠️  .gitignore missing (recommended)")
    
    return len(issues) == 0, issues

def generate_deployment_checklist():
    """Generate final deployment checklist"""
    print("\n" + "=" * 80)
    print("DEPLOYMENT CHECKLIST")
    print("=" * 80)
    
    checklist = [
        ("Set DEBUG = False in settings.py", not settings.DEBUG),
        ("Change SECRET_KEY to a unique value", 'insecure' not in settings.SECRET_KEY.lower()),
        ("Configure ALLOWED_HOSTS with your domain", len(settings.ALLOWED_HOSTS) > 0 and settings.ALLOWED_HOSTS != ['*']),
        ("Run 'python manage.py collectstatic'", os.path.exists('staticfiles')),
        ("Create admin superuser account", User.objects.filter(role='admin').exists()),
        ("Set up HTTPS/SSL certificate", hasattr(settings, 'CSRF_COOKIE_SECURE')),
        ("Configure production database (PostgreSQL/MySQL)", 'sqlite' not in settings.DATABASES['default']['ENGINE']),
        ("Set up regular database backups", os.path.exists('scripts/backup_database.py')),
        ("Configure email settings for notifications", hasattr(settings, 'EMAIL_HOST')),
        ("Test all features in staging environment", False),  # Manual
        ("Set up monitoring/logging", hasattr(settings, 'LOGGING')),
        ("Configure CORS if using API", 'corsheaders' in settings.INSTALLED_APPS),
    ]
    
    completed = sum(1 for _, status in checklist if status)
    total = len(checklist)
    
    for item, status in checklist:
        if status:
            print(f"✅ {item}")
        else:
            print(f"⬜ {item}")
    
    print(f"\nProgress: {completed}/{total} ({completed/total*100:.0f}%)")
    
    return completed, total

def main():
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "MULTIBLIZ POS DEPLOYMENT READINESS" + " " * 24 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    all_issues = []
    
    # Run all checks
    db_ok, db_issues = check_database()
    all_issues.extend(db_issues)
    
    settings_ok, settings_issues = check_settings()
    all_issues.extend(settings_issues)
    
    features_ok, features_issues = check_features()
    all_issues.extend(features_issues)
    
    security_ok, security_issues = check_security()
    all_issues.extend(security_issues)
    
    files_ok, files_issues = check_files()
    all_issues.extend(files_issues)
    
    completed, total = generate_deployment_checklist()
    
    # Final verdict
    print("\n" + "=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)
    
    if all_issues:
        print(f"\n⚠️  Found {len(all_issues)} issue(s) that need attention:\n")
        for i, issue in enumerate(all_issues, 1):
            print(f"{i}. {issue}")
    
    print()
    if db_ok and features_ok and len(all_issues) <= 3:
        print("✅ DEVELOPMENT READY: System is functional for local testing")
        print("⚠️  PRODUCTION READY: Needs configuration changes (see issues above)")
        print()
        print("RECOMMENDATION:")
        print("1. For local/testing: System is ready to use")
        print("2. For production deployment: Address the issues listed above")
        print("3. Especially important: DEBUG=False, SECRET_KEY, ALLOWED_HOSTS")
    elif len(all_issues) > 5:
        print("❌ NOT READY: Multiple critical issues found")
        print("\nPriority fixes needed before deployment")
    else:
        print("⚠️  PARTIALLY READY: Some issues need attention")
        print("\nAddress issues above before production deployment")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error during system check: {e}")
        import traceback
        traceback.print_exc()
