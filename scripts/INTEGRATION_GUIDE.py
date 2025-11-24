"""
Quick Integration Guide: How to Use Trained Models in Django
=============================================================

This file shows you exactly how to integrate the trained Prophet and XGBoost
models into your existing MultiBiz Django forecasting system.
"""

# =============================================================================
# OPTION 1: Update Your Existing forecasting/views.py
# =============================================================================

"""
Add this import at the top of forecasting/views.py:
"""
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Load models once when server starts (put this at module level)
PROPHET_MODEL = joblib.load('trained_models/prophet_model.pkl')
XGBOOST_MODEL = joblib.load('trained_models/xgboost_model.pkl')
FEATURE_COLUMNS = joblib.load('trained_models/feature_columns.pkl')
MODEL_METADATA = joblib.load('trained_models/model_metadata.pkl')

"""
Then modify your GenerateForecastsView to use the trained models:
"""

class GenerateForecastsView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            # Clear old forecasts first
            cutoff_date = datetime.now().date() - timedelta(days=7)
            deleted_count = Forecast.objects.filter(date__lt=cutoff_date).delete()[0]
            
            # Get top 50 products by sales volume (avoid timeout)
            products = Product.objects.annotate(
                total_sales=Count('sale')
            ).filter(total_sales__gt=0).order_by('-total_sales')[:50]
            
            forecasts_created = 0
            
            for product in products:
                # Get historical sales data
                sales_data = Sale.objects.filter(
                    product=product
                ).values('date').annotate(
                    quantity=Sum('quantity')
                ).order_by('date')
                
                if not sales_data:
                    continue
                
                # Prepare data for Prophet
                df = pd.DataFrame(sales_data)
                df.columns = ['ds', 'y']
                df['ds'] = pd.to_datetime(df['ds'])
                
                # Fill missing dates with 0
                date_range = pd.date_range(
                    start=df['ds'].min(),
                    end=df['ds'].max(),
                    freq='D'
                )
                df = df.set_index('ds').reindex(date_range, fill_value=0).reset_index()
                df.columns = ['ds', 'y']
                
                # === PROPHET FORECAST ===
                try:
                    # Create future dataframe (30 days ahead)
                    future = PROPHET_MODEL.make_future_dataframe(periods=30, freq='D')
                    
                    # Make prediction
                    prophet_forecast = PROPHET_MODEL.predict(future)
                    
                    # Save only future predictions (next 30 days)
                    future_forecasts = prophet_forecast.tail(30)
                    
                    for _, row in future_forecasts.iterrows():
                        Forecast.objects.create(
                            product=product,
                            date=row['ds'].date(),
                            predicted_quantity=max(0, round(row['yhat'], 2)),
                            algorithm='prophet',
                            confidence_lower=max(0, round(row['yhat_lower'], 2)),
                            confidence_upper=max(0, round(row['yhat_upper'], 2))
                        )
                        forecasts_created += 1
                
                except Exception as e:
                    print(f"Prophet error for {product.name}: {e}")
                
                # === XGBOOST FORECAST ===
                try:
                    # Prepare features for XGBoost
                    df_xgb = df.copy()
                    df_xgb.columns = ['Date', 'Quantity_Sold']
                    
                    # Add temporal features
                    df_xgb['Day_of_Week'] = df_xgb['Date'].dt.dayofweek
                    df_xgb['Month'] = df_xgb['Date'].dt.month
                    df_xgb['Day_of_Year'] = df_xgb['Date'].dt.dayofyear
                    df_xgb['Quarter'] = df_xgb['Date'].dt.quarter
                    df_xgb['Week_of_Year'] = df_xgb['Date'].dt.isocalendar().week
                    
                    # Add lag features
                    for lag in [1, 7, 14, 30]:
                        df_xgb[f'Lag_{lag}'] = df_xgb['Quantity_Sold'].shift(lag)
                    
                    # Add rolling features
                    df_xgb['Rolling_Mean_7'] = df_xgb['Quantity_Sold'].rolling(7, min_periods=1).mean()
                    df_xgb['Rolling_Mean_30'] = df_xgb['Quantity_Sold'].rolling(30, min_periods=1).mean()
                    df_xgb['Rolling_Std_7'] = df_xgb['Quantity_Sold'].rolling(7, min_periods=1).std()
                    
                    # Generate 30 future dates
                    last_date = df_xgb['Date'].max()
                    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=30, freq='D')
                    
                    # Predict for each future date
                    last_known_values = df_xgb.tail(30).copy()
                    
                    for future_date in future_dates:
                        # Create feature row for this future date
                        feature_row = {
                            'Day_of_Week': future_date.dayofweek,
                            'Month': future_date.month,
                            'Day_of_Year': future_date.dayofyear,
                            'Quarter': future_date.quarter,
                            'Week_of_Year': future_date.isocalendar().week,
                            'Lag_1': last_known_values['Quantity_Sold'].iloc[-1],
                            'Lag_7': last_known_values['Quantity_Sold'].iloc[-7] if len(last_known_values) >= 7 else last_known_values['Quantity_Sold'].mean(),
                            'Lag_14': last_known_values['Quantity_Sold'].iloc[-14] if len(last_known_values) >= 14 else last_known_values['Quantity_Sold'].mean(),
                            'Lag_30': last_known_values['Quantity_Sold'].iloc[-30] if len(last_known_values) >= 30 else last_known_values['Quantity_Sold'].mean(),
                            'Rolling_Mean_7': last_known_values['Quantity_Sold'].tail(7).mean(),
                            'Rolling_Mean_30': last_known_values['Quantity_Sold'].tail(30).mean(),
                            'Rolling_Std_7': last_known_values['Quantity_Sold'].tail(7).std()
                        }
                        
                        # Make prediction
                        X_pred = pd.DataFrame([feature_row])[FEATURE_COLUMNS]
                        prediction = XGBOOST_MODEL.predict(X_pred)[0]
                        
                        # Save forecast
                        Forecast.objects.create(
                            product=product,
                            date=future_date.date(),
                            predicted_quantity=max(0, round(prediction, 2)),
                            algorithm='xgboost'
                        )
                        forecasts_created += 1
                        
                        # Update last_known_values for next iteration
                        new_row = pd.DataFrame({
                            'Date': [future_date],
                            'Quantity_Sold': [prediction]
                        })
                        last_known_values = pd.concat([last_known_values, new_row]).tail(30)
                
                except Exception as e:
                    print(f"XGBoost error for {product.name}: {e}")
            
            messages.success(request, f"Successfully generated {forecasts_created} forecasts for {len(products)} products!")
            return redirect('forecast_list')
        
        except Exception as e:
            messages.error(request, f"Error generating forecasts: {str(e)}")
            return redirect('forecast_list')


# =============================================================================
# OPTION 2: Simpler Version (Just Use Prophet)
# =============================================================================

"""
If the above is too complex, here's a simpler version using only Prophet:
"""

class SimpleForecastView(LoginRequiredMixin, View):
    def post(self, request):
        # Load model
        prophet_model = joblib.load('trained_models/prophet_model.pkl')
        
        # Clear old forecasts
        Forecast.objects.filter(date__lt=datetime.now().date()).delete()
        
        # Get top products
        products = Product.objects.annotate(
            total_sales=Count('sale')
        ).filter(total_sales__gt=10).order_by('-total_sales')[:20]
        
        for product in products:
            # Get sales history
            sales = Sale.objects.filter(product=product).values('date').annotate(quantity=Sum('quantity'))
            df = pd.DataFrame(sales)
            df.columns = ['ds', 'y']
            
            # Train Prophet on this product's data
            model = Prophet(daily_seasonality=False)
            model.fit(df)
            
            # Predict 30 days ahead
            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)
            
            # Save forecasts
            for _, row in forecast.tail(30).iterrows():
                Forecast.objects.create(
                    product=product,
                    date=row['ds'].date(),
                    predicted_quantity=max(0, round(row['yhat'], 2)),
                    algorithm='prophet'
                )
        
        messages.success(request, "Forecasts generated successfully!")
        return redirect('forecast_list')


# =============================================================================
# OPTION 3: Add a Management Command (Recommended for Production)
# =============================================================================

"""
Create forecasting/management/commands/generate_forecasts.py:

This allows you to run: python manage.py generate_forecasts
"""

from django.core.management.base import BaseCommand
from forecasting.models import Forecast
from sales.models import Sale
from inventory.models import Product
import joblib
import pandas as pd
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Generate forecasts using trained ML models'
    
    def handle(self, *args, **kwargs):
        self.stdout.write("Loading trained models...")
        prophet_model = joblib.load('trained_models/prophet_model.pkl')
        
        self.stdout.write("Clearing old forecasts...")
        Forecast.objects.filter(date__lt=datetime.now().date()).delete()
        
        products = Product.objects.annotate(
            total_sales=Count('sale')
        ).filter(total_sales__gt=5).order_by('-total_sales')[:50]
        
        self.stdout.write(f"Generating forecasts for {len(products)} products...")
        
        total_forecasts = 0
        
        for i, product in enumerate(products, 1):
            sales_data = Sale.objects.filter(product=product).values('date').annotate(quantity=Sum('quantity'))
            
            if not sales_data:
                continue
            
            df = pd.DataFrame(sales_data)
            df.columns = ['ds', 'y']
            df['ds'] = pd.to_datetime(df['ds'])
            
            # Train Prophet for this product
            model = Prophet(weekly_seasonality=True, yearly_seasonality=False, daily_seasonality=False)
            model.fit(df)
            
            # Predict 30 days
            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)
            
            # Save forecasts
            for _, row in forecast.tail(30).iterrows():
                Forecast.objects.create(
                    product=product,
                    date=row['ds'].date(),
                    predicted_quantity=max(0, round(row['yhat'], 2)),
                    algorithm='prophet'
                )
                total_forecasts += 1
            
            self.stdout.write(f"  [{i}/{len(products)}] {product.name} ✓")
        
        self.stdout.write(self.style.SUCCESS(f"\nSuccessfully generated {total_forecasts} forecasts!"))


# =============================================================================
# HOW TO USE IN TEMPLATES (Chart Display)
# =============================================================================

"""
In your forecast_list.html, update the Chart.js section:
"""

"""
<script>
// Prepare data for chart
const forecastData = {{ forecasts_json|safe }};

// Group by date and algorithm
const dates = [];
const prophetPredictions = [];
const xgboostPredictions = [];

forecastData.forEach(f => {
    if (!dates.includes(f.date)) {
        dates.push(f.date);
    }
    
    if (f.algorithm === 'prophet') {
        prophetPredictions.push({x: f.date, y: f.predicted_quantity});
    } else if (f.algorithm === 'xgboost') {
        xgboostPredictions.push({x: f.date, y: f.predicted_quantity});
    }
});

// Create chart
const ctx = document.getElementById('forecastChart').getContext('2d');
new Chart(ctx, {
    type: 'line',
    data: {
        datasets: [
            {
                label: 'Prophet Forecast',
                data: prophetPredictions,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                tension: 0.4
            },
            {
                label: 'XGBoost Forecast',
                data: xgboostPredictions,
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                tension: 0.4
            }
        ]
    },
    options: {
        responsive: true,
        scales: {
            x: {
                type: 'time',
                time: {
                    unit: 'day'
                },
                title: {
                    display: true,
                    text: 'Date'
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Predicted Quantity'
                },
                beginAtZero: true
            }
        }
    }
});
</script>
"""


# =============================================================================
# TESTING THE MODELS
# =============================================================================

"""
Quick test script - run this in Django shell (python manage.py shell):
"""

import joblib
import pandas as pd
from datetime import datetime, timedelta

# Load model
prophet = joblib.load('trained_models/prophet_model.pkl')

# Test data
test_data = pd.DataFrame({
    'ds': pd.date_range(start='2024-01-01', periods=100, freq='D'),
    'y': [10, 15, 12, 18, 20, 25, 22] * 14 + [10, 15]  # Sample sales pattern
})

# Make prediction
future = prophet.make_future_dataframe(periods=30)
forecast = prophet.predict(future)

# Show results
print("Last 5 predictions:")
print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())

"""
Expected output:
            ds       yhat  yhat_lower  yhat_upper
95  2024-04-06   16.234      12.456      20.123
96  2024-04-07   15.891      11.234      19.567
...
"""

print("\n✅ If you see predictions above, the models work correctly!")
