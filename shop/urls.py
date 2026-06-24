from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # AJAX Cart routes
    path('cart/add/', views.cart_add, name='cart_add'),
    path('cart/remove/', views.cart_remove, name='cart_remove'),
    path('cart/update/', views.cart_update, name='cart_update'),
    path('cart/toggle-wishlist/', views.toggle_wishlist, name='wishlist_toggle'),
    
    # Coupon and Checkout
    path('coupon/validate/', views.validate_coupon, name='coupon_validate'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('payment/upi-verify/', views.upi_verify_view, name='upi_verify'),
]
