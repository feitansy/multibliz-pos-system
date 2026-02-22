# ============================================================================
# MULTIBLIZ ML TRAINING SCRIPT FOR GOOGLE COLAB
# ============================================================================
# Copy and paste this entire script into a Google Colab cell
# This trains XGBoost and Prophet models for demand forecasting
# ============================================================================

# STEP 1: Install packages
print("📦 Installing packages...")
import subprocess
import sys

packages = ['pandas', 'numpy', 'scikit-learn', 'xgboost', 'prophet', 'joblib', 'seaborn', 'matplotlib']
for package in packages:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', package])

print("✓ All packages installed!\n")

# STEP 2: Mount Google Drive
from google.colab import drive
import os

print("📁 Mounting Google Drive...")
drive.mount('/content/drive')

# Update this path to your folder
project_path = '/content/drive/MyDrive/Multibliz POS System'
if os.path.exists(project_path):
    os.chdir(project_path)
    print(f"✓ Working directory: {os.getcwd()}\n")
else:
    print(f"⚠️ Folder not found at: {project_path}")
    print("Please update the project_path variable\n")

# STEP 3: Import libraries
print("📚 Importing libraries...")
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import xgboost as xgb
from prophet import Prophet
import joblib
import warnings
import sys
from contextlib import contextmanager

warnings.filterwarnings('ignore')

# Configure plotting
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 6)
print("✓ Libraries imported!\n")

# STEP 4: Helper functions
@contextmanager
def suppress_stdout_stderr():
    """Suppress Prophet verbose output"""
    save_stdout = sys.stdout
    save_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    try:
        yield
    finally:
        sys.stdout = save_stdout
        sys.stderr = save_stderr

# STEP 5: Load or generate data
print("=" * 80)
print("LOADING DATA")
print("=" * 80)

try:
    df = pd.read_csv('data/datasets/Filtered_Printing_Business.csv', encoding='latin-1')
    print(f"✓ Loaded from CSV: {len(df)} records\n")
except FileNotFoundError:
    print("⚠️ CSV not found. Generating synthetic data...\n")
    
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    data = []
    
    for date in dates:
        day_type = date.dayofweek
        base_quantity = 15 if day_type < 5 else 8
        quantity = base_quantity + np.random.normal(0, 3) + np.sin(date.dayofyear / 365 * 2 * np.pi) * 5
        quantity = max(0, int(quantity))
        
        if quantity > 0:
            data.append({
                'Order Date': date,
                'Quantity': quantity,
                'Sales': quantity * np.random.uniform(100, 500),
                'Category': np.random.choice(['Paper', 'Binders', 'Labels', 'Art', 'Fasteners']),
            })
    
    df = pd.DataFrame(data)
    print(f"✓ Generated synthetic data: {len(df)} records\n")

# STEP 6: Data preparation
print("=" * 80)
print("PREPARING DATA")
print("=" * 80)

df['Order Date'] = pd.to_datetime(df['Order Date'])

daily_sales = df.groupby('Order Date').agg({
    'Quantity': 'sum',
    'Sales': 'sum'
}).reset_index()

daily_sales.columns = ['Date', 'Quantity_Sold', 'Sales_Value']

date_range = pd.date_range(start=daily_sales['Date'].min(), 
                           end=daily_sales['Date'].max(), 
                           freq='D')
daily_sales = daily_sales.set_index('Date').reindex(date_range, fill_value=0).reset_index()
daily_sales.columns = ['Date', 'Quantity_Sold', 'Sales_Value']

print(f"📊 Daily consumption statistics:")
print(f"   Total days: {len(daily_sales)}")
print(f"   Average daily: {daily_sales['Quantity_Sold'].mean():.2f} units")
print(f"   Max daily: {daily_sales['Quantity_Sold'].max():.0f} units")
print(f"   Min daily: {daily_sales['Quantity_Sold'].min():.0f} units\n")

# STEP 7: Feature engineering
print("=" * 80)
print("FEATURE ENGINEERING")
print("=" * 80)

xgb_data = daily_sales.copy()

# Temporal features
xgb_data['Day_of_Week'] = xgb_data['Date'].dt.dayofweek
xgb_data['Month'] = xgb_data['Date'].dt.month
xgb_data['Day_of_Year'] = xgb_data['Date'].dt.dayofyear
xgb_data['Quarter'] = xgb_data['Date'].dt.quarter
xgb_data['Week_of_Year'] = xgb_data['Date'].dt.isocalendar().week

# Lag features
for lag in [1, 7, 14, 30]:
    xgb_data[f'Lag_{lag}'] = xgb_data['Quantity_Sold'].shift(lag)

# Rolling statistics
xgb_data['Rolling_Mean_7'] = xgb_data['Quantity_Sold'].rolling(window=7, min_periods=1).mean()
xgb_data['Rolling_Mean_30'] = xgb_data['Quantity_Sold'].rolling(window=30, min_periods=1).mean()
xgb_data['Rolling_Std_7'] = xgb_data['Quantity_Sold'].rolling(window=7, min_periods=1).std()

xgb_data = xgb_data.dropna()

print("✓ Features created:")
print(f"   Temporal: Day_of_Week, Month, Day_of_Year, Quarter, Week_of_Year")
print(f"   Lags: 1, 7, 14, 30 days")
print(f"   Rolling: 7-day and 30-day stats")
print(f"   Final size: {len(xgb_data)} days\n")

# STEP 8: Train Prophet
print("=" * 80)
print("TRAINING PROPHET MODEL")
print("=" * 80)

prophet_data = daily_sales[['Date', 'Quantity_Sold']].copy()
prophet_data.columns = ['ds', 'y']

print("Training Prophet (this may take 1-2 minutes)...\n")

prophet_model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,
    changepoint_prior_scale=0.05,
    seasonality_prior_scale=10.0,
    interval_width=0.95
)

prophet_model.add_seasonality(name='quarterly', period=91.25, fourier_order=5)

with suppress_stdout_stderr():
    prophet_model.fit(prophet_data)

print("✓ Prophet model trained!\n")

# STEP 9: Train XGBoost
print("=" * 80)
print("TRAINING XGBOOST MODEL")
print("=" * 80)

feature_columns = ['Day_of_Week', 'Month', 'Day_of_Year', 'Quarter', 'Week_of_Year',
                   'Lag_1', 'Lag_7', 'Lag_14', 'Lag_30',
                   'Rolling_Mean_7', 'Rolling_Mean_30', 'Rolling_Std_7']

X = xgb_data[feature_columns]
y = xgb_data['Quantity_Sold']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

print(f"Training set: {len(X_train)} samples")
print(f"Test set: {len(X_test)} samples\n")

xgb_model = xgb.XGBRegressor(
    objective='reg:squarederror',
    n_estimators=200,
    learning_rate=0.05,
    max_depth=6,
    min_child_weight=3,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1,
    verbosity=0
)

print("Training XGBoost...\n")
xgb_model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

print("✓ XGBoost model trained!\n")

# STEP 10: Evaluate models
print("=" * 80)
print("MODEL EVALUATION")
print("=" * 80)

# Prophet evaluation
future_dates = prophet_model.make_future_dataframe(periods=0)
prophet_forecast = prophet_model.predict(future_dates)

prophet_predictions = prophet_forecast[['ds', 'yhat']].merge(prophet_data, on='ds', how='inner')
prophet_mae = mean_absolute_error(prophet_predictions['y'], prophet_predictions['yhat'])
prophet_rmse = np.sqrt(mean_squared_error(prophet_predictions['y'], prophet_predictions['yhat']))

print(f"\n📅 PROPHET MODEL:")
print(f"   MAE:  {prophet_mae:.2f} units")
print(f"   RMSE: {prophet_rmse:.2f} units")

# XGBoost evaluation
y_pred_train = xgb_model.predict(X_train)
y_pred_test = xgb_model.predict(X_test)

xgb_mae_train = mean_absolute_error(y_train, y_pred_train)
xgb_rmse_train = np.sqrt(mean_squared_error(y_train, y_pred_train))
xgb_mae_test = mean_absolute_error(y_test, y_pred_test)
xgb_rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))

print(f"\n🚀 XGBOOST MODEL:")
print(f"   Training MAE:  {xgb_mae_train:.2f} units")
print(f"   Training RMSE: {xgb_rmse_train:.2f} units")
print(f"   Test MAE:      {xgb_mae_test:.2f} units")
print(f"   Test RMSE:     {xgb_rmse_test:.2f} units")

if xgb_mae_test > xgb_mae_train * 1.5:
    print("\n⚠️  WARNING: Possible overfitting detected")
else:
    print("\n✓ Model generalizes well (no overfitting)\n")

# STEP 11: Feature importance
print("=" * 80)
print("FEATURE IMPORTANCE (Top 10)")
print("=" * 80)

feature_importance = pd.DataFrame({
    'Feature': feature_columns,
    'Importance': xgb_model.feature_importances_
}).sort_values('Importance', ascending=False)

print("\n" + feature_importance.head(10).to_string(index=False))
print("\n")

# STEP 12: Visualizations
print("=" * 80)
print("GENERATING VISUALIZATIONS")
print("=" * 80)

# Plot 1: Daily consumption trend
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(daily_sales['Date'], daily_sales['Quantity_Sold'], linewidth=1.5, color='#2E86AB')
ax.set_title('Daily Consumption Over Time', fontsize=14, fontweight='bold')
ax.set_xlabel('Date', fontweight='bold')
ax.set_ylabel('Quantity (Units)', fontweight='bold')
ax.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
print("✓ Daily consumption plot\n")

# Plot 2: Predictions vs Actual
test_dates = xgb_data.iloc[-len(y_test):]['Date'].values

fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# XGBoost
axes[0].plot(test_dates, y_test.values, label='Actual', linewidth=2, color='#2E86AB', marker='o', markersize=4)
axes[0].plot(test_dates, y_pred_test, label='XGBoost', linewidth=2, color='#A23B72', linestyle='--', marker='s', markersize=4)
axes[0].set_title(f'XGBoost: Predicted vs Actual\nMAE: {xgb_mae_test:.2f}', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Date', fontweight='bold')
axes[0].set_ylabel('Quantity (Units)', fontweight='bold')
axes[0].legend(fontsize=10)
axes[0].grid(True, alpha=0.3)
axes[0].tick_params(axis='x', rotation=45)

# Prophet
prophet_test = prophet_predictions.tail(len(y_test))
axes[1].plot(prophet_test['ds'], prophet_test['y'], label='Actual', linewidth=2, color='#2E86AB', marker='o', markersize=4)
axes[1].plot(prophet_test['ds'], prophet_test['yhat'], label='Prophet', linewidth=2, color='#06A77D', linestyle='--', marker='^', markersize=4)
axes[1].fill_between(prophet_test['ds'], prophet_test['yhat_lower'], prophet_test['yhat_upper'], 
                     alpha=0.2, color='#06A77D', label='95% CI')
axes[1].set_title(f'Prophet: Predicted vs Actual\nMAE: {prophet_mae:.2f}', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Date', fontweight='bold')
axes[1].set_ylabel('Quantity (Units)', fontweight='bold')
axes[1].legend(fontsize=10)
axes[1].grid(True, alpha=0.3)
axes[1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.show()
print("✓ Predictions vs actual plot\n")

# Plot 3: Feature importance
fig, ax = plt.subplots(figsize=(10, 6))
top_features = feature_importance.head(10)
ax.barh(top_features['Feature'], top_features['Importance'], color='#F18F01')
ax.set_xlabel('Importance Score', fontweight='bold')
ax.set_ylabel('Feature', fontweight='bold')
ax.set_title('XGBoost: Top 10 Features', fontsize=14, fontweight='bold')
ax.invert_yaxis()
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.show()
print("✓ Feature importance plot\n")

# STEP 13: Future forecasts
print("=" * 80)
print("GENERATING 30-DAY FORECASTS")
print("=" * 80)

last_date = daily_sales['Date'].max()
forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=30, freq='D')

# XGBoost forecasts
xgb_future_preds = []
for forecast_date in forecast_dates:
    features = pd.DataFrame([{
        'Day_of_Week': forecast_date.dayofweek,
        'Month': forecast_date.month,
        'Day_of_Year': forecast_date.dayofyear,
        'Quarter': forecast_date.quarter,
        'Week_of_Year': forecast_date.isocalendar()[1],
        'Lag_1': y.iloc[-1] if len(y) > 0 else y.mean(),
        'Lag_7': y.iloc[-7] if len(y) > 6 else y.mean(),
        'Lag_14': y.iloc[-14] if len(y) > 13 else y.mean(),
        'Lag_30': y.iloc[-30] if len(y) > 29 else y.mean(),
        'Rolling_Mean_7': y.tail(7).mean(),
        'Rolling_Mean_30': y.tail(30).mean(),
        'Rolling_Std_7': y.tail(7).std()
    }])
    
    pred = max(0, int(xgb_model.predict(features)[0]))
    xgb_future_preds.append(pred)

# Prophet forecasts
future = prophet_model.make_future_dataframe(periods=30)
with suppress_stdout_stderr():
    prophet_future_forecast = prophet_model.predict(future)

prophet_future = prophet_future_forecast[prophet_future_forecast['ds'] > last_date]
prophet_future_preds = [max(0, int(val)) for val in prophet_future['yhat'].values]

forecast_summary = pd.DataFrame({
    'Date': forecast_dates,
    'XGBoost': xgb_future_preds,
    'Prophet': prophet_future_preds,
    'Average': [int((x + y) / 2) for x, y in zip(xgb_future_preds, prophet_future_preds)]
})

print("\n30-Day Forecast (First 15 days):\n")
print(forecast_summary.head(15).to_string(index=False))
print(f"\nXGBoost Average:  {np.mean(xgb_future_preds):.0f} units/day")
print(f"Prophet Average:  {np.mean(prophet_future_preds):.0f} units/day")
print(f"Ensemble Average: {forecast_summary['Average'].mean():.0f} units/day\n")

# STEP 14: Save models
print("=" * 80)
print("SAVING MODELS TO GOOGLE DRIVE")
print("=" * 80)

models_dir = os.path.join(project_path, 'trained_models')
os.makedirs(models_dir, exist_ok=True)

joblib.dump(prophet_model, os.path.join(models_dir, 'prophet_model.pkl'))
print("✓ Saved: prophet_model.pkl")

joblib.dump(xgb_model, os.path.join(models_dir, 'xgboost_model.pkl'))
print("✓ Saved: xgboost_model.pkl")

joblib.dump(feature_columns, os.path.join(models_dir, 'feature_columns.pkl'))
print("✓ Saved: feature_columns.pkl")

metadata = {
    'training_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'data_points': len(daily_sales),
    'date_range': f"{daily_sales['Date'].min()} to {daily_sales['Date'].max()}",
    'prophet_mae': float(prophet_mae),
    'prophet_rmse': float(prophet_rmse),
    'xgboost_mae_test': float(xgb_mae_test),
    'xgboost_rmse_test': float(xgb_rmse_test),
    'feature_columns': feature_columns,
    'avg_daily_consumption': float(daily_sales['Quantity_Sold'].mean()),
    'max_daily_consumption': float(daily_sales['Quantity_Sold'].max())
}

joblib.dump(metadata, os.path.join(models_dir, 'model_metadata.pkl'))
print("✓ Saved: model_metadata.pkl")

forecast_summary.to_csv(os.path.join(models_dir, 'future_forecast_30days.csv'), index=False)
print("✓ Saved: future_forecast_30days.csv")

print(f"\n✓ All models saved to: {models_dir}\n")

# STEP 15: Generate report
print("=" * 80)
print("GENERATING TRAINING REPORT")
print("=" * 80)

report = f"""
{'='*80}
MULTIBLIZ FORECASTING - TRAINING REPORT
{'='*80}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Platform: Google Colab

{'='*80}
DATA SUMMARY
{'='*80}
Total Records: {len(df):,}
Total Days: {len(daily_sales)}
Date Range: {daily_sales['Date'].min()} to {daily_sales['Date'].max()}
Average Daily Consumption: {daily_sales['Quantity_Sold'].mean():.2f} units
Max Daily Consumption: {daily_sales['Quantity_Sold'].max():.0f} units

{'='*80}
MODEL PERFORMANCE
{'='*80}

PROPHET MODEL:
  MAE:  {prophet_mae:.2f} units
  RMSE: {prophet_rmse:.2f} units

XGBOOST MODEL:
  Training MAE:  {xgb_mae_train:.2f} units
  Training RMSE: {xgb_rmse_train:.2f} units
  Test MAE:      {xgb_mae_test:.2f} units
  Test RMSE:     {xgb_rmse_test:.2f} units

{'='*80}
TOP 5 IMPORTANT FEATURES
{'='*80}
{feature_importance.head(5).to_string(index=False)}

{'='*80}
NEXT STEPS
{'='*80}

1. Download Models:
   - Go to Google Drive → Multibliz POS System → trained_models
   - Download all .pkl files

2. Integrate into Django:
   - Copy models to: data/models/
   - Update forecasting/management/commands/auto_generate_forecast.py
   - Run: python manage.py auto_generate_forecast

3. View Forecasts:
   - Go to: http://localhost:8000/forecasting/
   - See 30-day predictions

4. Validation:
   - Run: python scripts/validate_forecasts.py
   - Monitor accuracy metrics

{'='*80}
"""

report_path = os.path.join(models_dir, 'training_report.txt')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report)

print(report)
print(f"✓ Report saved to: {report_path}\n")

# FINAL SUMMARY
print("=" * 80)
print("🎉 TRAINING COMPLETE!")
print("=" * 80)
print(f"""
✅ MODELS TRAINED:
   ✓ Prophet (Time-series with seasonality)
   ✓ XGBoost (Gradient boosting)
   ✓ Ensemble (Combined forecasts)

📊 PERFORMANCE:
   Prophet MAE:    {prophet_mae:.2f} units
   XGBoost MAE:    {xgb_mae_test:.2f} units (test)

📁 FILES SAVED TO GOOGLE DRIVE:
   ✓ trained_models/prophet_model.pkl
   ✓ trained_models/xgboost_model.pkl
   ✓ trained_models/feature_columns.pkl
   ✓ trained_models/model_metadata.pkl
   ✓ trained_models/future_forecast_30days.csv
   ✓ trained_models/training_report.txt

🚀 NEXT: Download from Google Drive and integrate into Django!
""")
print("=" * 80)
