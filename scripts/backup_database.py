"""
Automated Database Backup Script
Run this daily to backup your database
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import shutil
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent

def backup_database():
    """Backup SQLite database with timestamp"""
    
    # Create backups directory
    backup_dir = BASE_DIR / 'backups' / 'database'
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Source database
    db_path = BASE_DIR / 'db.sqlite3'
    
    if not db_path.exists():
        print("❌ Database file not found!")
        return False
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'db_backup_{timestamp}.sqlite3'
    backup_path = backup_dir / backup_name
    
    try:
        # Copy database file
        print(f"📦 Creating backup: {backup_name}")
        shutil.copy2(db_path, backup_path)
        
        # Verify backup
        if backup_path.exists():
            backup_size = backup_path.stat().st_size
            original_size = db_path.stat().st_size
            
            print(f"✅ Backup created successfully!")
            print(f"   Location: {backup_path}")
            print(f"   Size: {backup_size:,} bytes")
            print(f"   Original: {original_size:,} bytes")
            
            # Clean old backups (keep last 30)
            cleanup_old_backups(backup_dir, keep=30)
            
            return True
        else:
            print("❌ Backup file not created!")
            return False
            
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def cleanup_old_backups(backup_dir, keep=30):
    """Remove old backups, keeping only the most recent ones"""
    backups = sorted(backup_dir.glob('db_backup_*.sqlite3'), reverse=True)
    
    if len(backups) > keep:
        print(f"\n🗑️  Cleaning up old backups (keeping {keep} most recent)...")
        for old_backup in backups[keep:]:
            try:
                old_backup.unlink()
                print(f"   Deleted: {old_backup.name}")
            except Exception as e:
                print(f"   Failed to delete {old_backup.name}: {e}")

def list_backups():
    """List all available backups"""
    backup_dir = BASE_DIR / 'backups' / 'database'
    
    if not backup_dir.exists():
        print("No backups found.")
        return
    
    backups = sorted(backup_dir.glob('db_backup_*.sqlite3'), reverse=True)
    
    if not backups:
        print("No backups found.")
        return
    
    print(f"\n📋 Available Backups ({len(backups)}):")
    print("=" * 70)
    
    for i, backup in enumerate(backups[:10], 1):  # Show last 10
        size = backup.stat().st_size
        modified = datetime.fromtimestamp(backup.stat().st_mtime)
        print(f"{i}. {backup.name}")
        print(f"   Size: {size:,} bytes | Date: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

def restore_database(backup_name):
    """Restore database from backup"""
    backup_dir = BASE_DIR / 'backups' / 'database'
    backup_path = backup_dir / backup_name
    db_path = BASE_DIR / 'db.sqlite3'
    
    if not backup_path.exists():
        print(f"❌ Backup not found: {backup_name}")
        return False
    
    try:
        # Create backup of current database before restoring
        if db_path.exists():
            current_backup = BASE_DIR / 'backups' / 'database' / f'db_before_restore_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sqlite3'
            shutil.copy2(db_path, current_backup)
            print(f"📦 Current database backed up to: {current_backup.name}")
        
        # Restore from backup
        print(f"🔄 Restoring from: {backup_name}")
        shutil.copy2(backup_path, db_path)
        
        print(f"✅ Database restored successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Backup Manager')
    parser.add_argument('action', choices=['backup', 'list', 'restore'], 
                       help='Action to perform')
    parser.add_argument('--file', help='Backup file name (for restore)')
    
    args = parser.parse_args()
    
    if args.action == 'backup':
        backup_database()
    elif args.action == 'list':
        list_backups()
    elif args.action == 'restore':
        if not args.file:
            print("❌ Please specify backup file with --file parameter")
            list_backups()
        else:
            restore_database(args.file)
