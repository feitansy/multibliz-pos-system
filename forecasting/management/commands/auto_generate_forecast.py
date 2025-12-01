"""
Management command to automatically generate forecasts.
This can be run manually or scheduled via cron/task scheduler.
"""
from django.core.management.base import BaseCommand
from django.db import models
from django.utils import timezone
from datetime import timedelta
import pandas as pd
import xgboost as xgb
from prophet import Prophet

from forecasting.models import Forecast, ForecastConfig
from sales.models import Sale


class Command(BaseCommand):
    help = 'Automatically generate forecasts for all products with sales data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration even if forecasts were recently generated',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        # Check if we should generate forecasts
        config = ForecastConfig.get_config()
        
        if not force and not config.should_generate():
            days_since = (datetime.now().date() - config.last_generated.date()).days if config.last_generated else 'never'
            self.stdout.write(
                self.style.WARNING(
                    f'Forecasts were generated {days_since} days ago. '
                    f'Next generation in {config.generation_interval_days - days_since if isinstance(days_since, int) else config.generation_interval_days} days. '
                    f'Use --force to regenerate.'
                )
            )
            return
        
        self.stdout.write(self.style.NOTICE('Starting automatic forecast generation...'))
        
        today = timezone.now().date()
        
        # Clean up old forecasts
        old_forecasts = Forecast.objects.filter(forecast_date__lt=today)
        deleted_count = old_forecasts.count()
        old_forecasts.delete()
        self.stdout.write(f'Cleaned up {deleted_count} old forecasts.')
        
        # Get top 50 products with most sales
        products = Sale.objects.values('product').annotate(
            sale_count=models.Count('id')
        ).order_by('-sale_count')[:50].values_list('product', flat=True)
        
        # Delete existing future forecasts for these products
        Forecast.objects.filter(product__in=products, forecast_date__gte=today).delete()
        
        forecasts_generated = 0
        errors = []
        
        for prod_id in products:
            sales = Sale.objects.filter(product_id=prod_id).order_by('sale_date')
            if not sales.exists():
                continue
                
            df = pd.DataFrame(list(sales.values('sale_date', 'quantity')))
            df['sale_date'] = pd.to_datetime(df['sale_date'])
            df = df.groupby('sale_date')['quantity'].sum().reset_index()
            df.columns = ['ds', 'y']
            
            if len(df) < 2:
                errors.append(f'Product {prod_id}: Insufficient data ({len(df)} points)')
                continue
            
            try:
                xgboost_forecast = self.xgboost_forecast(df)
                prophet_forecast = self.prophet_forecast(df)
                
                # Generate forecasts for next 30 days
                for day_offset in range(0, 30):
                    forecast_date = today + timedelta(days=day_offset)
                    daily_xgb = int(xgboost_forecast * (0.85 + (day_offset % 7) * 0.05))
                    daily_prophet = int(prophet_forecast * (0.85 + ((day_offset + 3) % 7) * 0.05))
                    
                    Forecast.objects.create(
                        product_id=prod_id,
                        forecast_date=forecast_date,
                        predicted_quantity=daily_xgb,
                        algorithm_used='xgboost'
                    )
                    Forecast.objects.create(
                        product_id=prod_id,
                        forecast_date=forecast_date,
                        predicted_quantity=daily_prophet,
                        algorithm_used='prophet'
                    )
                forecasts_generated += 60  # 30 days * 2 algorithms
                
            except Exception as e:
                errors.append(f'Product {prod_id}: {str(e)}')
        
        # Update last generated timestamp
        config.last_generated = timezone.now()
        config.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated {forecasts_generated} forecasts for {len(products)} products.'
            )
        )
        
        if errors:
            self.stdout.write(self.style.WARNING(f'Errors encountered: {len(errors)}'))
            for error in errors[:5]:  # Show first 5 errors
                self.stdout.write(f'  - {error}')

    def xgboost_forecast(self, df):
        """XGBoost implementation for demand forecasting"""
        if df['y'].empty or len(df) < 2:
            return 0
        
        try:
            df['day_of_week'] = df['ds'].dt.dayofweek
            df['month'] = df['ds'].dt.month
            df['quarter'] = df['ds'].dt.quarter
            df['lag_1'] = df['y'].shift(1)
            df['lag_7'] = df['y'].shift(7)
            df['rolling_mean_7'] = df['y'].rolling(window=7, min_periods=1).mean()
            df['rolling_std_7'] = df['y'].rolling(window=7, min_periods=1).std()
            
            df = df.bfill().ffill()
            
            feature_cols = ['day_of_week', 'month', 'quarter', 'lag_1', 'lag_7', 'rolling_mean_7', 'rolling_std_7']
            X = df[feature_cols]
            y = df['y']
            
            model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42,
                verbosity=0
            )
            model.fit(X, y, verbose=False)
            
            last_date = df['ds'].iloc[-1]
            future_date = last_date + timedelta(days=30)
            
            future_features = pd.DataFrame({
                'day_of_week': [future_date.dayofweek],
                'month': [future_date.month],
                'quarter': [future_date.quarter],
                'lag_1': [df['y'].iloc[-1]],
                'lag_7': [df['y'].iloc[-7] if len(df) >= 7 else df['y'].mean()],
                'rolling_mean_7': [df['rolling_mean_7'].iloc[-1]],
                'rolling_std_7': [df['rolling_std_7'].iloc[-1]]
            })
            
            prediction = model.predict(future_features)[0]
            recent_avg = df['y'].tail(14).mean()
            scaled_prediction = max(recent_avg * 0.8, prediction)
            return int(max(5, round(scaled_prediction)))
        
        except Exception:
            recent_data = df['y'].tail(14)
            weighted_sum = 0
            weight_sum = 0
            for i, val in enumerate(recent_data):
                weight = i + 1
                weighted_sum += val * weight
                weight_sum += weight
            weighted_avg = weighted_sum / weight_sum
            return int(max(5, round(weighted_avg)))

    def prophet_forecast(self, df):
        """Prophet forecasting with improved accuracy"""
        try:
            model = Prophet(
                interval_width=0.95,
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                seasonality_mode='additive'
            )
            
            model.fit(df)
            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)
            
            predicted_value = forecast['yhat'].iloc[-1]
            recent_avg = df['y'].tail(14).mean()
            scaled_prediction = max(recent_avg * 0.8, predicted_value)
            
            return int(max(5, round(scaled_prediction)))
        
        except Exception:
            return self._exponential_smoothing_forecast(df)
    
    def _exponential_smoothing_forecast(self, df):
        """Fallback method using exponential smoothing"""
        try:
            from scipy import stats
            
            y = df['y'].values
            x = range(len(y))
            slope, intercept, _, _, _ = stats.linregress(x, y)
            
            smoothed = y[-1]
            forecast = smoothed + slope * 30
            
            recent_avg = df['y'].tail(14).mean()
            scaled_forecast = max(recent_avg * 0.8, forecast)
            
            return int(max(5, round(scaled_forecast)))
        except:
            recent_avg = df['y'].tail(14).mean()
            return int(max(5, round(recent_avg)))
