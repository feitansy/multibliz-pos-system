"""
Forecast Validation Script
Compares forecasted values with actual historical data to assess realism
"""

import os
import django
import sys
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')
django.setup()

from sales.models import Sale, Product
from forecasting.models import Forecast
from django.db.models import Sum, Avg, Count, Max, Min
from django.utils import timezone

def validate_forecasts():
    print("=" * 80)
    print("FORECAST VALIDATION REPORT")
    print("=" * 80)
    print()
    
    # Get historical statistics
    print("📊 HISTORICAL DATA ANALYSIS (Actual Sales)")
    print("-" * 80)
    
    # Overall statistics
    total_sales = Sale.objects.count()
    total_units = Sale.objects.aggregate(total=Sum('quantity'))['total'] or 0
    total_revenue = Sale.objects.aggregate(total=Sum('total_price'))['total'] or 0
    
    if total_sales == 0:
        print("⚠️  No historical sales data found!")
        return
    
    print(f"Total Sales Transactions: {total_sales:,}")
    print(f"Total Units Sold: {total_units:,}")
    print(f"Total Revenue: ₱{total_revenue:,.2f}")
    print(f"Average Units per Sale: {total_units/total_sales:.2f}")
    print(f"Average Revenue per Sale: ₱{total_revenue/total_sales:,.2f}")
    print()
    
    # Last 30 days statistics
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_sales = Sale.objects.filter(sale_date__gte=thirty_days_ago)
    recent_count = recent_sales.count()
    recent_units = recent_sales.aggregate(total=Sum('quantity'))['total'] or 0
    recent_revenue = recent_sales.aggregate(total=Sum('total_price'))['total'] or 0
    
    print("📅 LAST 30 DAYS (Actual)")
    print("-" * 80)
    print(f"Sales Transactions: {recent_count:,}")
    print(f"Total Units: {recent_units:,}")
    print(f"Total Revenue: ₱{recent_revenue:,.2f}")
    print(f"Daily Average Transactions: {recent_count/30:.1f}")
    print(f"Daily Average Units: {recent_units/30:.1f}")
    print(f"Daily Average Revenue: ₱{recent_revenue/30:,.2f}")
    print()
    
    # Product-level statistics
    print("🏆 TOP 5 PRODUCTS (Historical)")
    print("-" * 80)
    top_products = Sale.objects.values('product__name', 'product__price').annotate(
        total_units=Sum('quantity'),
        total_sales=Count('id'),
        total_revenue=Sum('total_price')
    ).order_by('-total_units')[:5]
    
    for i, prod in enumerate(top_products, 1):
        print(f"{i}. {prod['product__name']}")
        print(f"   Units Sold: {prod['total_units']:,}")
        print(f"   Transactions: {prod['total_sales']:,}")
        print(f"   Revenue: ₱{prod['total_revenue']:,.2f}")
        print(f"   Price: ₱{prod['product__price']:,.2f}")
        print()
    
    # Get forecast statistics
    forecasts = Forecast.objects.all()
    forecast_count = forecasts.count()
    
    if forecast_count == 0:
        print("⚠️  No forecasts found! Please generate forecasts first.")
        return
    
    print()
    print("🔮 FORECAST DATA ANALYSIS (Predictions)")
    print("-" * 80)
    
    # Next 30 days forecast
    today = timezone.now().date()
    thirty_days_future = today + timedelta(days=30)
    
    future_forecasts = forecasts.filter(
        forecast_date__gte=today,
        forecast_date__lte=thirty_days_future
    )
    
    forecast_units_xgb = future_forecasts.filter(algorithm_used='xgboost').aggregate(
        total=Sum('predicted_quantity')
    )['total'] or 0
    
    forecast_units_prophet = future_forecasts.filter(algorithm_used='prophet').aggregate(
        total=Sum('predicted_quantity')
    )['total'] or 0
    
    # Calculate average forecast
    avg_forecast_units = (forecast_units_xgb + forecast_units_prophet) / 2 if forecast_units_xgb and forecast_units_prophet else (forecast_units_xgb or forecast_units_prophet)
    
    # Get product prices for revenue calculation
    forecast_products = future_forecasts.values('product__name', 'product__price').annotate(
        xgb_units=Sum('predicted_quantity', filter=django.db.models.Q(algorithm_used='xgboost')),
        prophet_units=Sum('predicted_quantity', filter=django.db.models.Q(algorithm_used='prophet'))
    )
    
    forecast_revenue = 0
    for fp in forecast_products:
        avg_units = ((fp['xgb_units'] or 0) + (fp['prophet_units'] or 0)) / 2
        forecast_revenue += avg_units * float(fp['product__price'] or 0)
    
    print(f"Forecast Period: Next 30 days ({today} to {thirty_days_future})")
    print(f"XGBoost Predicted Units: {forecast_units_xgb:,.0f}")
    print(f"Prophet Predicted Units: {forecast_units_prophet:,.0f}")
    print(f"Average Predicted Units: {avg_forecast_units:,.0f}")
    print(f"Estimated Revenue: ₱{forecast_revenue:,.2f}")
    print()
    
    # Top forecasted products
    print("🔮 TOP 5 FORECASTED PRODUCTS (Next 30 days)")
    print("-" * 80)
    top_forecasts = forecasts.filter(
        forecast_date__gte=today,
        forecast_date__lte=thirty_days_future
    ).values('product__name', 'product__price').annotate(
        avg_units=Avg('predicted_quantity'),
        total_units=Sum('predicted_quantity')
    ).order_by('-total_units')[:5]
    
    for i, prod in enumerate(top_forecasts, 1):
        estimated_revenue = (prod['total_units'] or 0) * float(prod['product__price'] or 0)
        print(f"{i}. {prod['product__name']}")
        print(f"   Predicted Units: {prod['total_units']:,.0f}")
        print(f"   Daily Average: {prod['avg_units']:,.1f}")
        print(f"   Est. Revenue: ₱{estimated_revenue:,.2f}")
        print(f"   Price: ₱{prod['product__price']:,.2f}")
        print()
    
    # VALIDATION COMPARISON
    print()
    print("✅ VALIDATION: Historical vs Forecast Comparison")
    print("=" * 80)
    
    if recent_units > 0:
        # Compare daily averages
        historical_daily_units = recent_units / 30
        forecast_daily_units = avg_forecast_units / 30
        
        difference_units = forecast_daily_units - historical_daily_units
        percent_change = (difference_units / historical_daily_units * 100) if historical_daily_units > 0 else 0
        
        print("📈 DAILY UNIT COMPARISON:")
        print(f"   Historical (Last 30 days): {historical_daily_units:.1f} units/day")
        print(f"   Forecast (Next 30 days):   {forecast_daily_units:.1f} units/day")
        print(f"   Difference: {difference_units:+.1f} units/day ({percent_change:+.1f}%)")
        print()
        
        # Interpret results
        if abs(percent_change) <= 10:
            print("✅ ASSESSMENT: Forecasts are REALISTIC (within 10% of historical average)")
        elif abs(percent_change) <= 25:
            print("⚠️  ASSESSMENT: Forecasts show MODERATE deviation (10-25% from historical)")
        else:
            print("❌ ASSESSMENT: Forecasts show SIGNIFICANT deviation (>25% from historical)")
        print()
        
        # Revenue comparison
        historical_daily_revenue = float(recent_revenue) / 30
        forecast_daily_revenue = forecast_revenue / 30
        revenue_difference = forecast_daily_revenue - historical_daily_revenue
        revenue_percent = (revenue_difference / historical_daily_revenue * 100) if historical_daily_revenue > 0 else 0
        
        print("💰 DAILY REVENUE COMPARISON:")
        print(f"   Historical (Last 30 days): ₱{historical_daily_revenue:,.2f}/day")
        print(f"   Forecast (Next 30 days):   ₱{forecast_daily_revenue:,.2f}/day")
        print(f"   Difference: ₱{revenue_difference:+,.2f}/day ({revenue_percent:+.1f}%)")
        print()
        
    # Check for anomalies
    print("🔍 ANOMALY DETECTION:")
    print("-" * 80)
    
    # Check for products with extreme forecasts
    extreme_forecasts = []
    for product in Product.objects.all():
        hist_avg = Sale.objects.filter(
            product=product,
            sale_date__gte=thirty_days_ago
        ).aggregate(avg=Avg('quantity'))['avg'] or 0
        
        if hist_avg > 0:
            forecast_avg = forecasts.filter(
                product=product,
                forecast_date__gte=today,
                forecast_date__lte=thirty_days_future
            ).aggregate(avg=Avg('predicted_quantity'))['avg'] or 0
            
            if forecast_avg > 0:
                deviation = abs((forecast_avg - hist_avg) / hist_avg * 100)
                if deviation > 50:
                    extreme_forecasts.append({
                        'product': product.name,
                        'historical': hist_avg,
                        'forecast': forecast_avg,
                        'deviation': deviation
                    })
    
    if extreme_forecasts:
        print("⚠️  Products with extreme forecast deviations (>50%):")
        for ef in extreme_forecasts[:5]:
            print(f"   • {ef['product']}: {ef['historical']:.1f} → {ef['forecast']:.1f} units/day ({ef['deviation']:.0f}% change)")
    else:
        print("✅ No extreme deviations detected")
    
    print()
    print("=" * 80)
    print("RECOMMENDATIONS:")
    print("-" * 80)
    print("1. Monitor forecast accuracy by comparing with actual sales daily")
    print("2. Retrain models monthly with new data for improved accuracy")
    print("3. Investigate products with >50% deviation for potential trends")
    print("4. Use forecasts as guidance, not absolute predictions")
    print("5. Consider seasonal factors and market conditions")
    print("=" * 80)

if __name__ == '__main__':
    try:
        validate_forecasts()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
