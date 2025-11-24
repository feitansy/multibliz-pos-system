from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from sales.models import Sale
from inventory.models import Stock
from forecasting.models import Forecast
from .models import DashboardMetric
from django.db.models import Sum, Count, F
from datetime import datetime, timedelta
import json

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Sales metrics
        today = datetime.now().date()
        last_30_days = today - timedelta(days=30)
        last_60_days = today - timedelta(days=60)

        # Current period sales (last 30 days)
        total_sales_current = Sale.objects.filter(sale_date__date__gte=last_30_days).aggregate(
            total=Sum('total_price'), count=Count('id')
        )

        # Previous period sales (30-60 days ago) for KPI comparison
        total_sales_previous = Sale.objects.filter(
            sale_date__date__gte=last_60_days,
            sale_date__date__lt=last_30_days
        ).aggregate(total=Sum('total_price'), count=Count('id'))

        # Calculate KPI change percentage
        current_total = total_sales_current['total'] or 0
        previous_total = total_sales_previous['total'] or 0
        
        if previous_total > 0:
            sales_change = ((current_total - previous_total) / previous_total) * 100
        else:
            sales_change = 0 if current_total == 0 else 100

        # Recent sales - get last 5 sales
        recent_sales = Sale.objects.all().order_by('-sale_date')[:5]

        # Inventory metrics
        low_stock_items = Stock.objects.filter(quantity__lte=F('reorder_level'))

        # Forecast summary
        upcoming_forecasts = Forecast.objects.filter(forecast_date__gte=today)[:5]

        # 7-day sales trend data (for sparkline)
        seven_day_sales = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_total = Sale.objects.filter(sale_date__date=day).aggregate(
                total=Sum('total_price')
            )['total'] or 0
            seven_day_sales.append({
                'date': day.strftime('%a'),
                'amount': float(day_total)
            })

        # Sales by day of week for bar chart (last 30 days)
        sales_by_day = {}
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in days_of_week:
            sales_by_day[day] = 0

        sales_data = Sale.objects.filter(sale_date__date__gte=last_30_days).values('sale_date')
        for sale in sales_data:
            day_name = sale['sale_date'].strftime('%A')
            if day_name not in sales_by_day:
                sales_by_day[day_name] = 0
            sales_by_day[day_name] += 1

        context.update({
            'total_sales': current_total,
            'sales_count': total_sales_current['count'] or 0,
            'recent_sales': recent_sales,
            'low_stock_count': low_stock_items.count(),
            'upcoming_forecasts': upcoming_forecasts,
            'sales_change': round(sales_change, 1),
            'seven_day_sales': json.dumps(seven_day_sales),
            'sales_by_day': json.dumps(sales_by_day),
        })

        return context

class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/settings.html'


class AnalyticsDashboardView(LoginRequiredMixin, TemplateView):
    """
    Advanced Analytics Dashboard with Date Range Filtering
    
    Features:
    - Date range picker for custom period analysis
    - Sales trend line chart over selected period
    - Revenue breakdown by product category (pie chart)
    - Transaction count and average order value metrics
    - Top performing products
    - Export functionality (CSV)
    """
    template_name = 'dashboard/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get date range from query parameters
        from django.utils import timezone
        today = timezone.now().date()
        
        start_date_str = self.request.GET.get('start_date', (today - timedelta(days=30)).isoformat())
        end_date_str = self.request.GET.get('end_date', today.isoformat())
        
        try:
            from datetime import date
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except:
            start_date = today - timedelta(days=30)
            end_date = today

        # Get sales data for the period
        sales_in_period = Sale.objects.filter(
            sale_date__date__gte=start_date,
            sale_date__date__lte=end_date
        ).select_related('product')

        # ===== METRICS =====
        total_revenue = sales_in_period.aggregate(Sum('total_price'))['total_price__sum'] or 0
        transaction_count = sales_in_period.count()
        avg_order_value = total_revenue / transaction_count if transaction_count > 0 else 0
        
        # Calculate average daily revenue (total revenue divided by number of days in period)
        days_in_period = (end_date - start_date).days + 1
        avg_daily_revenue = total_revenue / days_in_period if days_in_period > 0 else 0

        # ===== SALES TREND (Daily) =====
        sales_trend = []
        current = start_date
        while current <= end_date:
            day_sales = sales_in_period.filter(
                sale_date__date=current
            ).aggregate(Sum('total_price'))['total_price__sum'] or 0
            
            sales_trend.append({
                'date': current.isoformat(),
                'revenue': float(day_sales),
                'count': sales_in_period.filter(sale_date__date=current).count()
            })
            current += timedelta(days=1)

        # ===== REVENUE BY CATEGORY =====
        revenue_by_category = {}
        for sale in sales_in_period:
            category = sale.product.category or 'Uncategorized'
            if category not in revenue_by_category:
                revenue_by_category[category] = 0
            revenue_by_category[category] += float(sale.total_price)

        # ===== TOP PRODUCTS =====
        top_products = {}
        for sale in sales_in_period:
            product_name = sale.product.name
            if product_name not in top_products:
                top_products[product_name] = {'quantity': 0, 'revenue': 0}
            top_products[product_name]['quantity'] += sale.quantity
            top_products[product_name]['revenue'] += float(sale.total_price)

        # Sort by revenue and get top 10
        top_products_sorted = sorted(
            top_products.items(),
            key=lambda x: x[1]['revenue'],
            reverse=True
        )[:10]

        context.update({
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_revenue': float(total_revenue),
            'transaction_count': transaction_count,
            'avg_order_value': float(avg_order_value),
            'avg_daily_revenue': float(avg_daily_revenue),
            'sales_trend': json.dumps(sales_trend),
            'revenue_by_category': json.dumps(revenue_by_category),
            'top_products': top_products_sorted,
        })

        return context

