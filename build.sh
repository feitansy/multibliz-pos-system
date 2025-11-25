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

# Import essential data (only 77 products with sales - lean version)
if [ -f "data_lean.json" ]; then
    python manage.py import_data --file=data_lean.json
fi
