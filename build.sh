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

# Import enhanced data (77 products + 1496 sales with historical data for forecasting)
if [ -f "data_enhanced.json" ]; then
    python manage.py import_data --file=data_enhanced.json
fi
