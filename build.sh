#!/usr/bin/env bash
# Exit on error
set -o errexit

# Set timeout for long-running operations (15 minutes max)
export BUILD_TIMEOUT=900

echo "==> Starting build process..."

# Install dependencies
echo "==> Installing dependencies..."
pip install -r requirements.txt --quiet

# Create media directory if it doesn't exist
mkdir -p media/products

# Collect static files
echo "==> Collecting static files..."
python manage.py collectstatic --noinput --clear --quiet

# Run migrations
echo "==> Running database migrations..."
python manage.py migrate --noinput

# Fix database sequences (if using PostgreSQL on Render)
echo "==> Fixing database sequences..."
python manage.py fix_db_sequences

# Create default admin user
echo "==> Creating default admin user..."
python manage.py create_default_admin

# Import enhanced data (77 products + 1496 sales with historical data for forecasting)
if [ -f "data_enhanced.json" ]; then
    echo "==> Importing data (this may take a few minutes)..."
    python manage.py import_data --file=data_enhanced.json
    
    # Fix sequences again after import (in case IDs got corrupted)
    echo "==> Fixing sequences after import..."
    python manage.py fix_db_sequences
fi

echo "==> Build complete! Forecast generation will run automatically on first dashboard access."
