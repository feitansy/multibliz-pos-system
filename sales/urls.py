from django.urls import path
from . import views

urlpatterns = [
    # POS Terminal
    path('pos/', views.POSView.as_view(), name='pos'),
    path('pos/test/', views.POSTestView.as_view(), name='pos_test'),
    path('api/search-products/', views.search_products, name='search_products'),
    path('api/process-transaction/', views.process_transaction, name='process_transaction'),
    
    # Product Management
    path('product/', views.ProductListView.as_view(), name='product_list'),
    path('product/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # Sales Records
    path('sale/', views.SaleListView.as_view(), name='sale_list'),
    path('sale/create/', views.SaleCreateView.as_view(), name='sale_create'),
    path('sale/<int:pk>/', views.SaleDetailView.as_view(), name='sale_detail'),
    path('sale/<int:pk>/update/', views.SaleUpdateView.as_view(), name='sale_update'),
    path('sale/<int:pk>/delete/', views.SaleDeleteView.as_view(), name='sale_delete'),
    path('sale/<int:pk>/receipt/', views.SaleReceiptView.as_view(), name='sale_receipt'),
    
    # Returns
    path('return/', views.ReturnListView.as_view(), name='return_list'),
    path('return/create/', views.ReturnCreateView.as_view(), name='return_create'),
    path('return/<int:pk>/', views.ReturnDetailView.as_view(), name='return_detail'),
    path('return/<int:pk>/update/', views.ReturnUpdateView.as_view(), name='return_update'),
]
