from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_overview, name='dashboard_overview'),
    path('orders/', views.dashboard_orders, name='dashboard_orders'),
    path('downloads/', views.dashboard_downloads, name='dashboard_downloads'),
    path('wishlist/', views.dashboard_wishlist, name='dashboard_wishlist'),
    path('coupons/', views.dashboard_coupons, name='dashboard_coupons'),
    path('profile/', views.dashboard_profile, name='dashboard_profile'),
    path('settings/', views.dashboard_settings, name='dashboard_settings'),
    
    # Custom Admin Control Room
    path('admin-analytics/', views.admin_analytics, name='admin_analytics'),
    path('admin-analytics/approve-upi/<int:order_id>/', views.admin_approve_upi, name='admin_approve_upi'),
    path('btc_dashboard/', views.btc_dashboard_view, name='btc_dashboard'),
]
