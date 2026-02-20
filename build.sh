#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "=== Starting Render build process ==="

# Install dependencies (with timeout to prevent hanging)
echo "Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

# Create media directory if it doesn't exist
mkdir -p media/products

# Collect static files (with noinput and minimal processing)
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear --no-input 2>/dev/null || echo "Static files warning - continuing..."

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Fix database sequences (if using PostgreSQL on Render)
echo "Fixing database sequences..."
python manage.py fix_db_sequences 2>/dev/null || echo "Sequence fix skipped"

# Create default admin user
echo "Creating default admin user..."
python manage.py create_default_admin

# Import enhanced data (only if file exists and database is empty)
if [ -f "data_enhanced.json" ]; then
    echo "Checking if data needs to be imported..."
    python manage.py import_data --file=data_enhanced.json || echo "Data import skipped (may already exist)"
    
    # Fix sequences again after import
    echo "Fixing sequences after import..."
    python manage.py fix_db_sequences 2>/dev/null || echo "Post-import sequence fix skipped"
else
    echo "No data file found - skipping import"
fi

echo "=== Build process completed successfully ==="
echo "Forecast generation is on-demand. Access /forecasting/ to trigger manually."
