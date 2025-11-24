"""
Quick Production Setup Script
Automates common deployment tasks
"""

import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def run_command(command, description):
    """Run a command and print status"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(command, shell=True, check=True, cwd=BASE_DIR)
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e}")
        return False

def check_env_file():
    """Check if .env file exists"""
    env_file = BASE_DIR / '.env'
    if not env_file.exists():
        print("\n⚠️  Warning: .env file not found!")
        print("Creating from .env.example...")
        example_file = BASE_DIR / '.env.example'
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            print("✅ Created .env file. Please edit it with your production values.")
        return False
    return True

def main():
    print("\n" + "="*60)
    print("🚀 MULTIBLIZ POS - PRODUCTION DEPLOYMENT SETUP")
    print("="*60)
    
    # Check Python version
    print(f"\n📌 Python Version: {sys.version}")
    
    # Check .env file
    if not check_env_file():
        print("\n⚠️  Please configure .env file before proceeding!")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    steps = []
    
    # Step 1: Install dependencies
    if run_command(
        "pip install -r requirements.txt",
        "Installing dependencies"
    ):
        steps.append("✅ Dependencies installed")
    else:
        steps.append("❌ Dependencies installation failed")
    
    # Step 2: Run migrations
    if run_command(
        "python manage.py migrate",
        "Running database migrations"
    ):
        steps.append("✅ Database migrated")
    else:
        steps.append("❌ Database migration failed")
    
    # Step 3: Collect static files
    if run_command(
        "python manage.py collectstatic --noinput",
        "Collecting static files"
    ):
        steps.append("✅ Static files collected")
    else:
        steps.append("❌ Static files collection failed")
    
    # Step 4: Run deployment checks
    if run_command(
        "python manage.py check --deploy",
        "Running deployment checks"
    ):
        steps.append("✅ Deployment checks passed")
    else:
        steps.append("⚠️  Deployment checks found issues")
    
    # Summary
    print("\n" + "="*60)
    print("📊 DEPLOYMENT SUMMARY")
    print("="*60)
    for step in steps:
        print(step)
    
    print("\n" + "="*60)
    print("📝 NEXT STEPS:")
    print("="*60)
    print("1. Review .env file and update production values")
    print("2. Set DEBUG=False in .env")
    print("3. Configure ALLOWED_HOSTS with your domain")
    print("4. Set up production database (PostgreSQL)")
    print("5. Configure web server (Nginx/Apache + Gunicorn)")
    print("6. Set up SSL certificate (Let's Encrypt)")
    print("7. Configure regular database backups")
    print("8. Set up monitoring and logging")
    print("\n📚 See DEPLOYMENT.md for detailed instructions")
    print("="*60)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment setup interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
