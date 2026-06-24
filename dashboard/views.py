from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from django.core.mail import send_mail

from shop.models import Order, OrderItem, Wishlist, Coupon, Product
from core.models import User

@login_required
def dashboard_overview(request):
    user_orders = Order.objects.filter(user=request.user)
    completed_orders = user_orders.filter(is_paid=True)
    
    # Calculate spending
    total_spending = completed_orders.aggregate(total=Sum('grand_total'))['total'] or 0.00
    
    # Count metrics
    orders_count = user_orders.count()
    downloads_count = OrderItem.objects.filter(order__user=request.user, order__is_paid=True).count()
    wishlist_count = Wishlist.objects.filter(user=request.user).count()
    
    context = {
        'orders_count': orders_count,
        'downloads_count': downloads_count,
        'wishlist_count': wishlist_count,
        'total_spending': total_spending,
        'recent_orders': user_orders.order_by('-created_at')[:5],
    }
    return render(request, 'dashboard/overview.html', context)


@login_required
def dashboard_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard/orders.html', {'orders': orders})


@login_required
def dashboard_downloads(request):
    # Fetch purchased items
    purchased_items = OrderItem.objects.filter(
        order__user=request.user,
        order__is_paid=True
    ).select_related('product')
    
    return render(request, 'dashboard/downloads.html', {'purchased_items': purchased_items})


@login_required
def dashboard_wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'dashboard/wishlist.html', {'wishlist_items': wishlist_items})


@login_required
def dashboard_coupons(request):
    # Show active coupons. Include user-exclusive and public coupons.
    public_coupons = Coupon.objects.filter(is_active=True, users__isnull=True)
    exclusive_coupons = Coupon.objects.filter(is_active=True, users=request.user)
    
    coupons = (public_coupons | exclusive_coupons).distinct().order_by('expiry_date')
    return render(request, 'dashboard/coupons.html', {'coupons': coupons})


@login_required
def dashboard_profile(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        
        messages.success(request, "Profile updated successfully.")
        return redirect('dashboard_profile')
        
    return render(request, 'dashboard/profile.html')


# Custom Admin Analytics Dashboard
def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin, login_url='login')
def admin_analytics(request):
    # Key business stats
    completed_orders = Order.objects.filter(is_paid=True)
    total_revenue = completed_orders.aggregate(total=Sum('grand_total'))['total'] or 0.00
    
    total_orders = Order.objects.count()
    completed_orders_count = completed_orders.count()
    conversion_rate = (completed_orders_count / total_orders * 100) if total_orders > 0 else 0.0
    
    total_users = User.objects.count()
    
    # Analytics charts datasets (Grouped completed sales for Chart.js)
    # Monthly sales stats
    monthly_sales = (
        completed_orders
        .values('created_at__month')
        .annotate(revenue=Sum('grand_total'))
        .order_by('created_at__month')
    )
    # Daily sales stats
    daily_sales = (
        completed_orders
        .values('created_at__date')
        .annotate(revenue=Sum('grand_total'))
        .order_by('created_at__date')[:15]
    )

    # Convert group query results to JSON arrays for Chart.js
    monthly_labels = [f"Month {item['created_at__month']}" for item in monthly_sales]
    monthly_values = [float(item['revenue']) for item in monthly_sales]
    
    daily_labels = [str(item['created_at__date']) for item in daily_sales]
    daily_values = [float(item['revenue']) for item in daily_sales]

    # Best-selling products list
    best_sellers = (
        OrderItem.objects.filter(order__is_paid=True)
        .values('product__title', 'product__price')
        .annotate(units_sold=Sum('quantity'), total_sales=Sum('price'))
        .order_by('-units_sold')[:5]
    )

    # Pending manual offline payments waiting for admin approval
    pending_upi_orders = Order.objects.filter(
        upi_verification_requested=True,
        is_paid=False
    ).order_by('-created_at')

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'completed_orders_count': completed_orders_count,
        'conversion_rate': conversion_rate,
        'total_users': total_users,
        'best_sellers': best_sellers,
        'pending_upi_orders': pending_upi_orders,
        'recent_orders': Order.objects.order_by('-created_at')[:10],
        'monthly_labels_json': json.dumps(monthly_labels),
        'monthly_values_json': json.dumps(monthly_values),
        'daily_labels_json': json.dumps(daily_labels),
        'daily_values_json': json.dumps(daily_values),
    }
    return render(request, 'dashboard/admin_analytics.html', context)


@user_passes_test(is_admin, login_url='login')
def admin_approve_upi(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if not order.is_paid:
        order.is_paid = True
        order.status = 'completed'
        order.save()
        
        # Increase coupon counts if any
        if order.coupon:
            order.coupon.used_count += 1
            order.coupon.save()

        # Send Invoice notification
        send_mail(
            f"Payment Verified: Order {order.order_id}",
            f"Hi {order.user.username},\n\nWe have manually verified your UPI transaction (UTR: {order.upi_utr}). Your payment of ₹{order.grand_total} has been confirmed. You can now download your digital products from the User Dashboard.",
            'no-reply@bobbythecoder.in',
            [order.user.email],
            fail_silently=True
        )
        messages.success(request, f"Order {order.order_id} has been manually approved and is marked as paid!")
    else:
        messages.warning(request, "This order is already marked as paid.")
        
    return redirect('admin_analytics')
