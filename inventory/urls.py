from django.urls import path
from . import views

urlpatterns = [
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/create/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier_detail'),
    path('suppliers/<int:pk>/update/', views.SupplierUpdateView.as_view(), name='supplier_update'),
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),
    path('stocks/', views.StockListView.as_view(), name='stock_list'),
    path('stocks/print-report/', views.InventoryPrintReportView.as_view(), name='inventory_print_report'),
    path('stocks/create/', views.StockCreateView.as_view(), name='stock_create'),
    path('stocks/<int:pk>/', views.StockDetailView.as_view(), name='stock_detail'),
    path('stocks/<int:pk>/update/', views.StockUpdateView.as_view(), name='stock_update'),
    path('stocks/<int:pk>/delete/', views.StockDeleteView.as_view(), name='stock_delete'),
]
