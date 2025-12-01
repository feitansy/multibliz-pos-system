from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
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
        
        return Forecast.objects.select_related('product').filter(
            forecast_date__gte=seven_days_ago
        ).order_by('-forecast_date', '-created_at')
    
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
