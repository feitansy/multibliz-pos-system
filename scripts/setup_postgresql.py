#!/usr/bin/env python
"""
PostgreSQL Setup and Migration Script
Helps migrate from SQLite to PostgreSQL for production deployment.
"""
import os
import sys
import json
import subprocess
from pathlib import Path

# Add the project directory to the path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')
import django
django.setup()

from django.core.management import call_command
from django.db import connection
from django.conf import settings


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def check_postgresql_installed():
    """Check if PostgreSQL is installed and accessible"""
    print_header("CHECKING POSTGRESQL INSTALLATION")
    
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ PostgreSQL not found in system PATH")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL not installed or not in system PATH")
        print("\n📥 Download PostgreSQL from: https://www.postgresql.org/download/")
        print("   Recommended: PostgreSQL 15 or 16")
        return False


def test_postgresql_connection():
    """Test connection to PostgreSQL database"""
    print_header("TESTING POSTGRESQL CONNECTION")
    
    if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.postgresql':
        print("❌ PostgreSQL not configured in settings")
        print("   Configure DB_ENGINE in .env file first")
        return False
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ Connected to PostgreSQL!")
            print(f"   Version: {version}")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\n🔧 Common issues:")
        print("   1. Check PostgreSQL service is running")
        print("   2. Verify database credentials in .env")
        print("   3. Ensure database exists (create it first)")
        print("   4. Check PostgreSQL allows local connections")
        return False


def create_database_guide():
    """Show guide for creating PostgreSQL database"""
    print_header("CREATING POSTGRESQL DATABASE")
    
    db_name = os.getenv('DB_NAME', 'multibliz_pos')
    db_user = os.getenv('DB_USER', 'postgres')
    
    print("📝 Steps to create the database:")
    print("\n1. Open PostgreSQL command line (psql):")
    print("   Windows: Search 'SQL Shell (psql)' in Start Menu")
    print("   Or run: psql -U postgres")
    
    print(f"\n2. Create database and user:")
    print(f"   CREATE DATABASE {db_name};")
    print(f"   CREATE USER {db_user} WITH PASSWORD 'your_password';")
    print(f"   ALTER ROLE {db_user} SET client_encoding TO 'utf8';")
    print(f"   ALTER ROLE {db_user} SET default_transaction_isolation TO 'read committed';")
    print(f"   ALTER ROLE {db_user} SET timezone TO 'Asia/Manila';")
    print(f"   GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};")
    
    print("\n3. Update .env file with your credentials")
    print("   Uncomment and set: DB_ENGINE, DB_NAME, DB_USER, DB_PASSWORD, etc.")
    
    print("\n4. Run this script again to test connection")


def migrate_database():
    """Run Django migrations on PostgreSQL"""
    print_header("RUNNING DATABASE MIGRATIONS")
    
    try:
        print("📦 Creating database tables...")
        call_command('migrate', '--noinput')
        print("✅ Migrations completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False


def export_sqlite_data():
    """Export data from SQLite database"""
    print_header("EXPORTING DATA FROM SQLITE")
    
    sqlite_db = BASE_DIR / 'db.sqlite3'
    if not sqlite_db.exists():
        print("❌ SQLite database not found")
        return None
    
    export_file = BASE_DIR / 'data_export.json'
    
    try:
        print(f"📤 Exporting data to {export_file}...")
        
        # Temporarily switch to SQLite
        original_engine = settings.DATABASES['default']['ENGINE']
        settings.DATABASES['default'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': sqlite_db,
        }
        
        # Export data
        with open(export_file, 'w') as f:
            call_command('dumpdata', 
                        '--natural-foreign', 
                        '--natural-primary',
                        '--exclude=contenttypes',
                        '--exclude=auth.permission',
                        '--indent=2',
                        stdout=f)
        
        # Restore original settings
        settings.DATABASES['default']['ENGINE'] = original_engine
        
        print(f"✅ Data exported successfully!")
        print(f"   File: {export_file}")
        return export_file
    except Exception as e:
        print(f"❌ Export failed: {str(e)}")
        return None


def import_postgresql_data(export_file):
    """Import data into PostgreSQL database"""
    print_header("IMPORTING DATA TO POSTGRESQL")
    
    if not export_file or not os.path.exists(export_file):
        print("❌ Export file not found")
        return False
    
    try:
        print(f"📥 Importing data from {export_file}...")
        call_command('loaddata', export_file)
        print("✅ Data imported successfully!")
        
        # Clean up export file
        os.remove(export_file)
        print("🧹 Cleaned up temporary export file")
        return True
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        print(f"   Export file preserved at: {export_file}")
        return False


def create_superuser_if_needed():
    """Check if admin user exists, prompt to create if not"""
    from accounts.models import User
    
    if not User.objects.filter(role='admin').exists():
        print_header("CREATING ADMIN USER")
        print("⚠️  No admin user found in database")
        print("   Creating superuser...")
        
        try:
            call_command('createsuperuser')
            print("✅ Superuser created!")
        except Exception as e:
            print(f"⚠️  Superuser creation skipped or failed: {str(e)}")


def verify_migration():
    """Verify that migration was successful"""
    print_header("VERIFYING MIGRATION")
    
    try:
        from inventory.models import Product
        from sales.models import Sale
        from accounts.models import User
        
        product_count = Product.objects.count()
        sale_count = Sale.objects.count()
        user_count = User.objects.count()
        
        print(f"✅ Database verification:")
        print(f"   Products: {product_count}")
        print(f"   Sales: {sale_count}")
        print(f"   Users: {user_count}")
        
        if product_count == 0 and sale_count == 0:
            print("\n⚠️  Database is empty - this is normal for a fresh installation")
            print("   You can import your SQLite data or start fresh")
        
        return True
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False


def main():
    """Main setup workflow"""
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "POSTGRESQL SETUP & MIGRATION" + " " * 30 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Step 1: Check if PostgreSQL is installed
    if not check_postgresql_installed():
        print("\n❌ Please install PostgreSQL first, then run this script again")
        return
    
    # Step 2: Check if PostgreSQL is configured
    if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.postgresql':
        print("\n⚠️  PostgreSQL not configured in .env file")
        create_database_guide()
        print("\n💡 After configuration, run: python scripts/setup_postgresql.py")
        return
    
    # Step 3: Test connection
    if not test_postgresql_connection():
        create_database_guide()
        return
    
    print("\n✅ PostgreSQL is configured and accessible!")
    
    # Step 4: Ask user about migration
    print("\n" + "=" * 80)
    print("MIGRATION OPTIONS")
    print("=" * 80)
    print("\n1. Fresh install (create empty database)")
    print("2. Migrate from SQLite (import existing data)")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == '1':
        # Fresh install
        if migrate_database():
            create_superuser_if_needed()
            verify_migration()
            print("\n✅ Fresh PostgreSQL database created successfully!")
            
    elif choice == '2':
        # Migrate from SQLite
        export_file = export_sqlite_data()
        if export_file:
            if migrate_database():
                if import_postgresql_data(export_file):
                    verify_migration()
                    print("\n✅ Migration from SQLite completed successfully!")
                    print("\n📝 Next steps:")
                    print("   1. Test your application with PostgreSQL")
                    print("   2. Backup your SQLite database (db.sqlite3) for safety")
                    print("   3. Update your deployment configuration")
                else:
                    print("\n⚠️  Data import failed - database structure created but empty")
            else:
                print("\n❌ Migration failed - check errors above")
    else:
        print("\n👋 Exiting...")
        return
    
    print("\n" + "=" * 80)
    print("🎉 PostgreSQL setup complete!")
    print("=" * 80)
    print("\n📚 For more information, see: DEPLOYMENT.md")


if __name__ == "__main__":
    main()
