from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Vendors
    path('vendors/', views.vendor_list, name='vendor_list'),
    path('vendors/add/', views.vendor_create, name='vendor_create'),
    path('vendors/<int:pk>/', views.vendor_detail, name='vendor_detail'),
    path('vendors/<int:pk>/edit/', views.vendor_edit, name='vendor_edit'),
    path('vendors/<int:pk>/delete/', views.vendor_delete, name='vendor_delete'),

    # Purchases
    path('purchases/', views.purchase_list, name='purchase_list'),
    path('purchases/add/', views.purchase_create, name='purchase_create'),
    path('purchases/<int:pk>/', views.purchase_detail, name='purchase_detail'),
    path('purchases/<int:pk>/edit/', views.purchase_edit, name='purchase_edit'),

    # Payments
    path('payments/add/', views.payment_create, name='payment_create'),
    path('payments/add/<int:purchase_pk>/', views.payment_create, name='payment_create_for_purchase'),

    # Analytics
    path('analytics/', views.analytics, name='analytics'),

    # Items
    path('items/', views.item_list, name='item_list'),
    path('items/add/', views.item_create, name='item_create'),
    path('items/edit/<int:pk>/', views.item_update, name='item_update'),
    path('items/delete/<int:pk>/', views.item_delete, name='item_delete'),

    # Export
    path('export/purchases/', views.export_purchases_csv, name='export_purchases'),
    path('export/vendors/', views.export_vendors_csv, name='export_vendors'),

    # API
    path('api/vendors/search/', views.api_vendor_search, name='api_vendor_search'),
    path('api/gst/', views.api_gst_calc, name='api_gst_calc'),
    path('api/risk/<int:vendor_pk>/', views.api_risk_score, name='api_risk_score'),
]