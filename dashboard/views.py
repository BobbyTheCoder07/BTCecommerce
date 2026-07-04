from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import json

from shop.models import Order, OrderItem, Wishlist, Coupon, Product, Category, Review
from core.models import User, NewsletterSubscriber, ContactMessage, Service, Testimonial
from blog.models import Post, Comment
from learn.models import Language, Topic

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
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            fail_silently=True
        )
        messages.success(request, f"Order {order.order_id} has been manually approved and is marked as paid!")
    else:
        messages.warning(request, "This order is already marked as paid.")
        
    return redirect('admin_analytics')


@login_required
def dashboard_settings(request):
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth import update_session_auth_hash
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard_settings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
        
    return render(request, 'dashboard/settings.html', {'form': form})


@user_passes_test(is_admin, login_url='login')
def btc_dashboard_view(request):
    # 1. Money tracking (Razorpay commission details)
    completed_orders = Order.objects.filter(is_paid=True)
    gross_revenue = completed_orders.aggregate(total=Sum('grand_total'))['total'] or 0.00
    
    # Razorpay standard: 2% of transaction value + 18% GST on the fee itself
    razorpay_fee_percentage = 0.02
    gst_percentage = 0.18
    
    commission_fees = float(gross_revenue) * razorpay_fee_percentage
    gst_fees = commission_fees * gst_percentage
    total_commission_deducted = commission_fees + gst_fees
    net_revenue = float(gross_revenue) - total_commission_deducted
    
    # 2. Coupon codes
    coupons = Coupon.objects.all()
    
    # Handle coupon code creation form directly from the dashboard
    if request.method == 'POST' and 'create_coupon' in request.POST:
        code = request.POST.get('code', '').strip().upper()
        discount_percentage = request.POST.get('discount_percentage', None)
        discount_flat = request.POST.get('discount_flat', None)
        usage_limit = request.POST.get('usage_limit', None)
        expiry_date = request.POST.get('expiry_date', None)
        
        if code:
            try:
                discount_percentage = int(discount_percentage) if discount_percentage else None
                discount_flat = float(discount_flat) if discount_flat else None
                usage_limit = int(usage_limit) if usage_limit else None
                
                Coupon.objects.create(
                    code=code,
                    discount_percentage=discount_percentage,
                    discount_flat=discount_flat,
                    usage_limit=usage_limit,
                    expiry_date=expiry_date if expiry_date else None
                )
                messages.success(request, f"Coupon code '{code}' created successfully!")
            except Exception as e:
                messages.error(request, f"Error creating coupon: {e}")
            return redirect('btc_dashboard')
            
    # 3. Models stats
    model_stats = [
        {"name": "Users", "count": User.objects.count(), "url": "/admin/core/user/"},
        {"name": "Products (Ebooks)", "count": Product.objects.count(), "url": "/admin/shop/product/"},
        {"name": "Orders", "count": Order.objects.count(), "url": "/admin/shop/order/"},
        {"name": "Coupons", "count": Coupon.objects.count(), "url": "/admin/shop/coupon/"},
        {"name": "Languages", "count": Language.objects.count(), "url": "/admin/learn/language/"},
        {"name": "Topics", "count": Topic.objects.count(), "url": "/admin/learn/topic/"},
        {"name": "Services", "count": Service.objects.count(), "url": "/admin/core/service/"},
        {"name": "Testimonials", "count": Testimonial.objects.count(), "url": "/admin/core/testimonial/"},
        {"name": "Blog Posts", "count": Post.objects.count(), "url": "/admin/blog/post/"},
        {"name": "Comments", "count": Comment.objects.count(), "url": "/admin/blog/comment/"},
        {"name": "Subscribers", "count": NewsletterSubscriber.objects.count(), "url": "/admin/core/newslettersubscriber/"},
        {"name": "Messages", "count": ContactMessage.objects.count(), "url": "/admin/core/contactmessage/"},
    ]
    
    # 4. Product-by-product earnings (Page-by-page analytics & earnings)
    products_analytics = []
    products = Product.objects.all()
    for prod in products:
        items = OrderItem.objects.filter(product=prod, order__is_paid=True)
        units_sold = items.aggregate(total_units=Sum('quantity'))['total_units'] or 0
        total_earnings = items.aggregate(total_cash=Sum('price'))['total_cash'] or 0.00
        
        # Calculate Razorpay fee for this product
        prod_commission = float(total_earnings) * razorpay_fee_percentage
        prod_gst = prod_commission * gst_percentage
        prod_deduction = prod_commission + prod_gst
        prod_net = float(total_earnings) - prod_deduction
        
        products_analytics.append({
            "title": prod.title,
            "category": prod.category.name,
            "units_sold": units_sold,
            "gross": total_earnings,
            "commission": prod_deduction,
            "net": prod_net
        })
        
    # 5. Blog Pageviews / Comment stats
    blog_analytics = []
    posts = Post.objects.all().order_by('-views')
    for post in posts:
        blog_analytics.append({
            "title": post.title,
            "category": post.get_category_display(),
            "views": post.views,
            "comments_count": post.comments.count(),
            "created_at": post.created_at
        })
        
    # Chart.js data
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

    monthly_labels = [f"Month {item['created_at__month']}" for item in monthly_sales]
    monthly_values = [float(item['revenue']) for item in monthly_sales]
    
    daily_labels = [str(item['created_at__date']) for item in daily_sales]
    daily_values = [float(item['revenue']) for item in daily_sales]
    
    # UPI verification list
    pending_upi_orders = Order.objects.filter(
        upi_verification_requested=True,
        is_paid=False
    ).order_by('-created_at')
    
    context = {
        # Money tracking
        'gross_revenue': gross_revenue,
        'commission_fees': commission_fees,
        'gst_fees': gst_fees,
        'total_commission_deducted': total_commission_deducted,
        'net_revenue': net_revenue,
        
        # Lists
        'coupons': coupons,
        'model_stats': model_stats,
        'products_analytics': products_analytics,
        'blog_analytics': blog_analytics,
        'pending_upi_orders': pending_upi_orders,
        'recent_orders': Order.objects.order_by('-created_at')[:10],
        
        # Chart JSON arrays
        'monthly_labels_json': json.dumps(monthly_labels),
        'monthly_values_json': json.dumps(monthly_values),
        'daily_labels_json': json.dumps(daily_labels),
        'daily_values_json': json.dumps(daily_values),
    }
    
    return render(request, 'dashboard/btc_dashboard.html', context)
