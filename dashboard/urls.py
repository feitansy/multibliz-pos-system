from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('system-settings/', views.SettingsView.as_view(), name='system_settings'),
    path('analytics/', views.AnalyticsDashboardView.as_view(), name='analytics'),
]
