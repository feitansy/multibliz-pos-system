from django.urls import path
from . import views

urlpatterns = [
    path('forecasts/', views.ForecastListView.as_view(), name='forecast_list'),
    path('forecasts/print-report/', views.ForecastPrintReportView.as_view(), name='forecast_print_report'),
    path('forecasts/<int:pk>/', views.ForecastDetailView.as_view(), name='forecast_detail'),
]
