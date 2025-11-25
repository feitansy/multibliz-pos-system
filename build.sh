#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate --noinput

# Create default admin user
python manage.py create_default_admin

# Import data from SQLite export (only runs if data_export.json exists)
if [ -f "data_export.json" ]; then
    python manage.py import_data --file=data_export.json
fi
