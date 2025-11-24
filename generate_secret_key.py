"""
Generate a strong SECRET_KEY for Django production deployment
Run this script and copy the output to your Railway environment variables
"""

from django.core.management.utils import get_random_secret_key

if __name__ == '__main__':
    secret_key = get_random_secret_key()
    print("\n" + "="*70)
    print("🔐 NEW SECRET KEY FOR PRODUCTION")
    print("="*70)
    print(f"\n{secret_key}\n")
    print("="*70)
    print("\n📋 Instructions:")
    print("1. Copy the key above")
    print("2. Go to Railway.app → Your Project → Variables")
    print("3. Add new variable: SECRET_KEY = <paste key here>")
    print("4. Save and redeploy")
    print("\n⚠️  IMPORTANT: Keep this key secret! Don't commit to Git!")
    print("="*70 + "\n")
