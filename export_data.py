#!/usr/bin/env python
"""Export data from SQLite with proper encoding handling"""
import os
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Force SQLite temporarily
os.environ['DB_ENGINE'] = 'django.db.backends.sqlite3'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')

import django
django.setup()

from django.core.management import call_command

print("📤 Exporting data from SQLite...")
with open('data_export.json', 'w', encoding='utf-8') as f:
    call_command(
        'dumpdata',
        '--natural-foreign',
        '--natural-primary',
        '--exclude=contenttypes',
        '--exclude=auth.permission',
        '--indent=2',
        stdout=f
    )

print("✅ Data exported to data_export.json")
