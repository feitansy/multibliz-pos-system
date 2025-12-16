#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate --noinput

# Fix database sequences (if using PostgreSQL on Render)
python manage.py fix_db_sequences

# Create default admin user
python manage.py create_default_admin

# Import enhanced data (77 products + 1496 sales with historical data for forecasting)
if [ -f "data_enhanced.json" ]; then
    python manage.py import_data --file=data_enhanced.json
    
    # Fix sequences again after import (in case IDs got corrupted)
    python manage.py fix_db_sequences
fi

# Generate initial forecasts (runs automatically every 30 days based on sales data)
# DISABLED: This command takes 10-15+ minutes and causes deployment timeouts on Render
# Forecasts are now generated on-demand via the dashboard or API
# python manage.py auto_generate_forecast --force || echo "Forecast generation skipped (may not have enough data yet)"
echo "Forecast generation is now on-demand. Run 'python manage.py auto_generate_forecast --force' manually if needed."
