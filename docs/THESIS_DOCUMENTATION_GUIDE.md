# MultiBiz Forecasting Models - Thesis Documentation Guide

## ✅ Training Completed Successfully!

### 📊 Model Performance Summary

| Model | MAE (Mean Absolute Error) | RMSE | Interpretation |
|-------|---------------------------|------|----------------|
| **Prophet** | 15.19 units | 19.91 units | Off by ±15 units per day on average |
| **XGBoost** | 18.27 units (test) | 23.61 units | Off by ±18 units per day on average |

### 🎯 Key Findings for Thesis

1. **Top 5 Most Important Features (XGBoost)**:
   - Rolling 7-day average (26.5%) - Most predictive!
   - Day of Week (10.6%) - Weekday vs weekend patterns
   - 14-day lag (10.3%) - Bi-weekly patterns
   - 7-day lag (9.5%) - Weekly patterns
   - Rolling 7-day standard deviation (7.9%) - Volatility matters

2. **What This Means**:
   - Recent consumption trends are the strongest predictor
   - Weekly patterns exist (busy days vs slow days)
   - Historical data from 1-2 weeks back helps predict future

### 📁 Files Generated (Use These in Your Thesis!)

**For Chapter 3 (Methodology):**
- `prophet_components.png` - Shows how Prophet decomposes data into trend + seasonality
- Screenshot the training pipeline output showing data preprocessing steps

**For Chapter 4 (Results):**
- `xgboost_predictions.png` - Visual proof your model works (predicted vs actual)
- `training_report.txt` - Performance metrics table
- `feature_importance.png` - Bar chart showing what matters most

**For Chapter 5 (Discussion):**
- Talk about the overfitting warning (XGBoost trained too well on training data)
- Suggest solutions: More data, regularization, cross-validation
- Discuss proxy data limitation (US vs PH seasonality)

### 🎓 Thesis Defense Q&A Prep

**Q: Why did you choose these two models?**
A: Prophet is designed for time-series with seasonality (captures weekly/yearly patterns). XGBoost handles complex non-linear relationships and learns from engineered features like lags and rolling averages. Using both provides robust predictions.

**Q: What is MAE/RMSE?**
A: 
- MAE = Average error in units (easier to interpret)
- RMSE = Penalizes large errors more (useful for detecting outliers)
- Lower is better for both

**Q: Why use US data instead of local data?**
A: Real Philippine printing shop data was unavailable for this academic project. I filtered the dataset to only office supplies relevant to printing (Paper, Binders, Labels). I acknowledge in my limitations section that local data would improve accuracy due to Philippine-specific seasonality (Thesis Season in March-May, different holiday patterns).

**Q: What is the overfitting warning?**
A: The model performed very well on training data (MAE 4.44) but worse on test data (MAE 18.27). This suggests it "memorized" training patterns instead of generalizing. Solutions include: collecting more data, using regularization, or cross-validation.

**Q: How will this help the printing shop owner?**
A: The system predicts daily consumption 30-90 days ahead. If current stock is 500 units and predicted consumption is 25 units/day, they'll run out in 20 days. The system alerts them to reorder before stockout.

### 💻 How to Integrate into Your Django System

```python
# In your forecasting/views.py or wherever you generate forecasts:

import joblib
import pandas as pd
from datetime import timedelta

# Load trained models (do this once at startup)
prophet_model = joblib.load('trained_models/prophet_model.pkl')
xgboost_model = joblib.load('trained_models/xgboost_model.pkl')
feature_columns = joblib.load('trained_models/feature_columns.pkl')

# To generate forecasts for a product:
def generate_forecast_for_product(product):
    # Get historical sales for this product
    sales = Sale.objects.filter(product=product).values('date', 'quantity')
    df = pd.DataFrame(sales)
    
    # Prepare data for Prophet
    prophet_data = df.rename(columns={'date': 'ds', 'quantity': 'y'})
    
    # Generate 30-day forecast
    future = prophet_model.make_future_dataframe(periods=30)
    forecast = prophet_model.predict(future)
    
    # Save forecasts to database
    for idx, row in forecast.tail(30).iterrows():
        Forecast.objects.create(
            product=product,
            date=row['ds'],
            predicted_quantity=row['yhat'],
            algorithm='prophet'
        )
```

### 📌 Important Thesis Sections to Include

**Limitations:**
- Using proxy data (US Superstore instead of local PH data)
- XGBoost shows signs of overfitting
- Limited to historical patterns (cannot predict unprecedented events)

**Future Work:**
- Collect real local printing shop sales data
- Implement cross-validation to reduce overfitting
- Add external features (weather, school calendar, economic indicators)
- Ensemble both models for better predictions

**Ethical Considerations:**
- Data privacy: Ensure sales data is anonymized
- Bias: US data may not represent Philippine consumption patterns
- Transparency: Shop owners should understand model limitations

### 🎯 Citations for Your References Section

```
Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. 
In Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge 
Discovery and Data Mining (pp. 785-794).

Taylor, S. J., & Letham, B. (2018). Forecasting at scale. 
The American Statistician, 72(1), 37-45.

Dataset: Superstore Sales Dataset. Retrieved from [Kaggle/source]
```

### ✨ Summary for Abstract/Executive Summary

> The MultiBiz system implements predictive forecasting using two complementary 
> machine learning algorithms: Prophet and XGBoost. Trained on 1,458 days of 
> historical sales data, the models achieved a Mean Absolute Error of 15-18 units 
> per day, enabling the system to predict supply consumption 30 days in advance. 
> This allows printing shop owners to optimize inventory levels, reduce stockouts, 
> and minimize carrying costs. Key predictive features include 7-day rolling 
> averages (26.5% importance) and day-of-week patterns (10.6% importance).

---

## 🚀 Next Steps for Your System

1. ✅ Models are trained and saved
2. ⏳ Integrate model loading into Django views
3. ⏳ Create forecast generation function
4. ⏳ Build dashboard to display predictions
5. ⏳ Add alerts for low stock based on predicted consumption
6. ⏳ Test with real printing shop if possible

Good luck with your thesis defense! 🎓
