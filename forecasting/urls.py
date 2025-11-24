from django.urls import path
from . import views

urlpatterns = [
    path('forecasts/', views.ForecastListView.as_view(), name='forecast_list'),
    path('forecasts/generate/', views.GenerateForecastView.as_view(), name='forecast_generate'),
    path('forecasts/generate/<int:product_id>/', views.GenerateForecastView.as_view(), name='generate_forecast'),
    path('forecasts/<int:pk>/', views.ForecastDetailView.as_view(), name='forecast_detail'),
]
