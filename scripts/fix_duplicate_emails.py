"""
Fix duplicate email addresses in the User model by keeping the most recent user
and updating duplicates with unique email addresses.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db.models import Count

User = get_user_model()

def fix_duplicate_emails():
    """Find and fix duplicate email addresses"""
    
    # Find duplicate emails
    duplicate_emails = User.objects.values('email').annotate(
        count=Count('id')
    ).filter(count__gt=1, email__isnull=False).exclude(email='')
    
    print("=" * 60)
    print("FIXING DUPLICATE EMAIL ADDRESSES")
    print("=" * 60)
    
    if not duplicate_emails:
        print("\n✓ No duplicate emails found!")
        return
    
    print(f"\nFound {len(duplicate_emails)} duplicate email(s)\n")
    
    for dup in duplicate_emails:
        email = dup['email']
        count = dup['count']
        
        print(f"\nEmail: {email} ({count} users)")
        print("-" * 60)
        
        # Get all users with this email, ordered by date (keep newest)
        users = User.objects.filter(email=email).order_by('-date_joined')
        
        # Keep the first (most recent) user
        keep_user = users.first()
        duplicate_users = users[1:]
        
        print(f"  ✓ Keeping: {keep_user.username} (ID: {keep_user.id}) - Joined: {keep_user.date_joined}")
        
        # Update duplicate users
        for i, user in enumerate(duplicate_users, 1):
            old_email = user.email
            new_email = f"{user.username}_{user.id}@duplicate.local"
            user.email = new_email
            user.save()
            print(f"  → Updated: {user.username} (ID: {user.id})")
            print(f"    Old email: {old_email}")
            print(f"    New email: {new_email}")
    
    print("\n" + "=" * 60)
    print("✓ DUPLICATE EMAILS FIXED!")
    print("=" * 60)
    
    # Verify no more duplicates
    remaining = User.objects.values('email').annotate(
        count=Count('id')
    ).filter(count__gt=1, email__isnull=False).exclude(email='')
    
    if remaining:
        print(f"\n⚠ Warning: Still have {len(remaining)} duplicate(s)")
    else:
        print("\n✓ All duplicates resolved!")

if __name__ == '__main__':
    try:
        fix_duplicate_emails()
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
