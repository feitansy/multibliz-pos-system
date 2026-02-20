#!/usr/bin/env bash
# Warmup script to run after deployment
# Generates forecasts after app is fully deployed

echo "==> Running post-deployment warmup..."

# Wait for app to be ready
sleep 5

# Generate initial forecasts (optional, runs asynchronously on first user request)
echo "==> Setup complete. Forecasts will be generated on first dashboard access."
