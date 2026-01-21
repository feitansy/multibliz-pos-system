from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import Q, Sum, F
from django.db.models.functions import TruncDate
from .models import Forecast, ForecastConfig
from sales.models import Sale
from datetime import datetime, timedelta
import json


class ForecastListView(LoginRequiredMixin, ListView):
    model = Forecast
    template_name = 'forecasting/forecast_list.html'
    context_object_name = 'forecasts'
    paginate_by = 60  # Show 60 forecasts per page (30 days × 2 algorithms)
    ordering = ['-forecast_date', '-created_at']
    
    def get_queryset(self):
        # Show only future forecasts and recent past (last 7 days)
        today = datetime.now().date()
        seven_days_ago = today - timedelta(days=7)
        
        queryset = Forecast.objects.select_related('product').filter(
            forecast_date__gte=seven_days_ago
        )
        
        # Apply product filter
        product_id = self.request.GET.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Apply algorithm filter
        algorithm = self.request.GET.get('algorithm')
        if algorithm and algorithm in ['xgboost', 'prophet']:
            queryset = queryset.filter(algorithm_used=algorithm)
        
        # Apply date range filter
        date_range = self.request.GET.get('date_range', 'all')
        if date_range == 'week':
            start_date = today - timedelta(days=7)
            queryset = queryset.filter(forecast_date__gte=start_date)
        elif date_range == 'month':
            start_date = today - timedelta(days=30)
            queryset = queryset.filter(forecast_date__gte=start_date)
        elif date_range == 'future':
            queryset = queryset.filter(forecast_date__gte=today)
        
        # Apply sorting
        sort_by = self.request.GET.get('sort_by', '-forecast_date')
        valid_sorts = [
            '-forecast_date', 'forecast_date',
            '-predicted_quantity', 'predicted_quantity',
            '-predicted_revenue', 'predicted_revenue',
            'algorithm_used', '-algorithm_used',
            'product__name', '-product__name'
        ]
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('-forecast_date', '-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Get historical sales data for the chart (last 30 days)
            today = datetime.now().date()
            thirty_days_ago = today - timedelta(days=30)
            
            sales_data = Sale.objects.filter(
                sale_date__date__gte=thirty_days_ago
            ).annotate(
                date=TruncDate('sale_date')
            ).values('date').annotate(
                total_quantity=models.Sum('quantity')
            ).order_by('date')
            
            # Format sales data for template (convert dates to strings)
            formatted_sales = []
            for item in sales_data:
                formatted_sales.append({
                    'sale_date__date': item['date'].strftime('%Y-%m-%d'),
                    'total_quantity': item['total_quantity']
                })
            
            context['historical_sales_json'] = json.dumps(formatted_sales)
            
            # Get aggregated forecast data for the chart (next 30 days)
            thirty_days_ahead = today + timedelta(days=30)
            
            forecast_data = Forecast.objects.filter(
                forecast_date__gte=today,
                forecast_date__lte=thirty_days_ahead
            ).values('forecast_date', 'algorithm_used').annotate(
                total_quantity=models.Sum('predicted_quantity')
            ).order_by('forecast_date', 'algorithm_used')
            
            # Format forecast data for template
            formatted_forecasts = []
            for item in forecast_data:
                formatted_forecasts.append({
                    'forecast_date': item['forecast_date'].strftime('%Y-%m-%d'),
                    'algorithm_used': item['algorithm_used'],
                    'total_quantity': item['total_quantity']
                })
            
            context['forecast_data_json'] = json.dumps(formatted_forecasts)
            
            # Calculate total projected revenue from future forecasts only (next 30 days)
            future_forecasts = Forecast.objects.filter(
                forecast_date__gte=today,
                forecast_date__lte=thirty_days_ahead
            ).select_related('product')
            
            total_revenue = sum(
                forecast.predicted_revenue 
                for forecast in future_forecasts
            )
            
            # Calculate total predicted units
            total_units = sum(
                forecast.predicted_quantity 
                for forecast in future_forecasts
            )
            
            context['total_projected_revenue'] = total_revenue
            context['total_predicted_units'] = total_units
            
            # Get unique products for filter dropdown
            context['all_products'] = Forecast.objects.values_list(
                'product_id', 'product__name'
            ).distinct().order_by('product__name')
            
            # Get filter parameters
            context['product_id_filter'] = self.request.GET.get('product_id', '')
            context['algorithm_filter'] = self.request.GET.get('algorithm', '')
            context['date_range_filter'] = self.request.GET.get('date_range', 'all')
            context['sort_by'] = self.request.GET.get('sort_by', '-forecast_date')
            
            # Add forecast generation status
            try:
                config = ForecastConfig.get_config()
                context['forecast_config'] = config
                context['last_generated'] = config.last_generated
                context['next_generation_days'] = config.days_until_next_generation()
                context['auto_generate_enabled'] = config.auto_generate_enabled
            except Exception:
                context['forecast_config'] = None
            
        except Exception as e:
            # If there's an error, provide empty data to prevent template errors
            context['historical_sales_json'] = '[]'
            context['forecast_data_json'] = '[]'
            context['total_projected_revenue'] = 0
            context['forecast_config'] = None
            print(f"Error fetching historical sales: {e}")
        
        return context


class ForecastDetailView(LoginRequiredMixin, DetailView):
    model = Forecast
    template_name = 'forecasting/forecast_detail.html'

class ForecastPrintReportView(LoginRequiredMixin, TemplateView):
    """
    Generate printable forecast report
    Includes all forecast predictions with filtering and sorting options
    """
    template_name = 'forecasting/forecast_print_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.now().date()
        seven_days_ago = today - timedelta(days=7)
        
        # Get forecasts with related product data
        forecasts = Forecast.objects.select_related('product').filter(
            forecast_date__gte=seven_days_ago
        )
        
        # Apply product filter
        product_id = self.request.GET.get('product_id')
        if product_id:
            forecasts = forecasts.filter(product_id=product_id)
        
        # Apply algorithm filter
        algorithm = self.request.GET.get('algorithm')
        if algorithm and algorithm in ['xgboost', 'prophet']:
            forecasts = forecasts.filter(algorithm_used=algorithm)
        
        # Apply date range filter
        date_range = self.request.GET.get('date_range', 'all')
        if date_range == 'week':
            start_date = today - timedelta(days=7)
            forecasts = forecasts.filter(forecast_date__gte=start_date)
        elif date_range == 'month':
            start_date = today - timedelta(days=30)
            forecasts = forecasts.filter(forecast_date__gte=start_date)
        elif date_range == 'future':
            forecasts = forecasts.filter(forecast_date__gte=today)
        
        # Apply sorting
        sort_by = self.request.GET.get('sort_by', '-forecast_date')
        valid_sorts = [
            '-forecast_date', 'forecast_date',
            '-predicted_quantity', 'predicted_quantity',
            'algorithm_used', '-algorithm_used',
            'product__name', '-product__name'
        ]
        if sort_by in valid_sorts:
            forecasts = forecasts.order_by(sort_by)
        else:
            forecasts = forecasts.order_by('-forecast_date', '-created_at')
        
        # Calculate summary statistics
        total_forecasts = forecasts.count()
        total_predicted_units = forecasts.aggregate(total=Sum('predicted_quantity'))['total'] or 0
        # Calculate revenue: Sum of (predicted_quantity * product.price)
        total_projected_revenue = sum([f.predicted_revenue for f in forecasts]) if forecasts else 0
        
        # Count by algorithm
        xgboost_count = forecasts.filter(algorithm_used='xgboost').count()
        prophet_count = forecasts.filter(algorithm_used='prophet').count()
        
        # Get unique products for filter dropdown
        all_products = Forecast.objects.values_list(
            'product_id', 'product__name'
        ).distinct().order_by('product__name')
        
        context['forecasts'] = forecasts
        context['total_forecasts'] = total_forecasts
        context['total_predicted_units'] = total_predicted_units
        context['total_projected_revenue'] = total_projected_revenue
        context['xgboost_count'] = xgboost_count
        context['prophet_count'] = prophet_count
        context['all_products'] = all_products
        context['product_id_filter'] = product_id or ''
        context['algorithm_filter'] = algorithm or ''
        context['date_range_filter'] = date_range
        context['sort_by'] = sort_by
        context['generated_date'] = datetime.now()
        
        return context