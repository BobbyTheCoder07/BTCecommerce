from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail

import json
import razorpay
import urllib.parse
from decimal import Decimal

from .models import Category, Product, Coupon, Order, OrderItem, Wishlist, Review

class ProductListView(ListView):
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Advanced Filtering
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        difficulty = self.request.GET.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)

        language = self.request.GET.get('language')
        if language:
            queryset = queryset.filter(programming_language=language)

        price_type = self.request.GET.get('price_type')
        if price_type == 'free':
            queryset = queryset.filter(is_free=True)
        elif price_type == 'paid':
            queryset = queryset.filter(is_free=False)

        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=Decimal(min_price))
        if max_price:
            queryset = queryset.filter(price__lte=Decimal(max_price))

        # Search Query
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)

        # Ordering
        sort = self.request.GET.get('sort', 'newest')
        if sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort == 'popular':
            queryset = queryset.order_by('-rating')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['languages'] = Product.LANGUAGE_CHOICES
        context['difficulties'] = Product.DIFFICULTY_CHOICES
        context['featured_products'] = Product.objects.filter(is_featured=True)[:3]
        # Keep selected filter values in context
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_difficulty'] = self.request.GET.get('difficulty', '')
        context['selected_language'] = self.request.GET.get('language', '')
        context['selected_price_type'] = self.request.GET.get('price_type', '')
        context['selected_sort'] = self.request.GET.get('sort', 'newest')
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Related Products in the same category
        context['related_products'] = Product.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id)[:3]
        
        # Check if user has purchased this product (to allow direct download)
        context['has_purchased'] = False
        if self.request.user.is_authenticated:
            context['has_purchased'] = OrderItem.objects.filter(
                order__user=self.request.user,
                order__is_paid=True,
                product=self.object
            ).exists()
            context['is_in_wishlist'] = Wishlist.objects.filter(
                user=self.request.user,
                product=self.object
            ).exists()
            
        context['reviews'] = self.object.reviews.order_by('-created_at')
        return context


def cart_add(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        qty = int(request.POST.get('qty', 1))
        
        product = get_object_or_404(Product, id=product_id)
        cart = request.session.get('cart', {})
        
        # Since digital products are usually 1 quantity max per user
        cart[str(product_id)] = 1
        request.session['cart'] = cart
        request.session.modified = True
        
        # Recalculate cart count
        cart_count = len(cart)
        return JsonResponse({
            'status': 'success',
            'message': f'{product.title} added to cart.',
            'cart_count': cart_count
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def cart_remove(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        cart = request.session.get('cart', {})
        
        if str(product_id) in cart:
            del cart[str(product_id)]
            request.session['cart'] = cart
            request.session.modified = True
            
        return JsonResponse({
            'status': 'success',
            'message': 'Item removed from cart.',
            'cart_count': len(cart)
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def cart_update(request):
    # For digital products, quantity is usually fixed to 1, but we keep this for consistency
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        qty = max(1, int(request.POST.get('qty', 1)))
        
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            cart[str(product_id)] = 1  # Cap digital items at 1
            request.session['cart'] = cart
            request.session.modified = True
            
        return JsonResponse({'status': 'success', 'message': 'Cart updated.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def toggle_wishlist(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to save items.'})
        
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if not created:
            wishlist_item.delete()
            return JsonResponse({'status': 'removed', 'message': 'Removed from wishlist.'})
            
        return JsonResponse({'status': 'added', 'message': 'Added to wishlist.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def validate_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        cart_total = float(request.POST.get('cart_total', 0.0))
        
        if not code:
            return JsonResponse({'status': 'error', 'message': 'Coupon code cannot be empty.'})
            
        try:
            coupon = Coupon.objects.get(code=code)
            valid, msg = coupon.is_valid(request.user)
            if not valid:
                return JsonResponse({'status': 'error', 'message': msg})
                
            discount = float(coupon.calculate_discount(Decimal(cart_total)))
            grand_total = max(0.00, cart_total - discount)
            
            # Save coupon code to user session
            request.session['applied_coupon'] = code
            
            return JsonResponse({
                'status': 'success',
                'message': 'Coupon applied successfully!',
                'discount': discount,
                'grand_total': grand_total,
                'code': code
            })
        except Coupon.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid coupon code.'})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required
def checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect('product_list')
        
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)
    
    total_amount = Decimal(0.0)
    for p in products:
        total_amount += p.current_price

    # Apply session coupon if any
    discount_amount = Decimal(0.0)
    coupon_code = request.session.get('applied_coupon')
    coupon_obj = None
    if coupon_code:
        try:
            coupon_obj = Coupon.objects.get(code=coupon_code)
            valid, _ = coupon_obj.is_valid(request.user)
            if valid:
                discount_amount = coupon_obj.calculate_discount(total_amount)
        except Coupon.DoesNotExist:
            request.session['applied_coupon'] = None

    # Calculate GST (18%) Structure
    taxable_value = total_amount - discount_amount
    gst_amount = taxable_value * Decimal(0.18)
    grand_total = taxable_value + gst_amount

    # Create Order Staged
    order = Order.objects.create(
        user=request.user,
        coupon=coupon_obj,
        total_amount=total_amount,
        discount_amount=discount_amount,
        gst_amount=gst_amount,
        grand_total=grand_total,
        status='pending'
    )
    
    for p in products:
        OrderItem.objects.create(
            order=order,
            product=p,
            price=p.current_price,
            quantity=1
        )

    # Razorpay Order Creation
    razorpay_order_id = None
    client_key = settings.RAZORPAY_KEY_ID
    
    if grand_total > 0 and client_key != 'rzp_test_your_dummy_key_id':
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            data = {
                "amount": int(grand_total * 100),  # in paise
                "currency": "INR",
                "receipt": str(order.order_id),
                "payment_capture": 1
            }
            razorpay_order = client.order.create(data=data)
            razorpay_order_id = razorpay_order['id']
            order.razorpay_order_id = razorpay_order_id
            order.save()
        except Exception as e:
            # Fallback if Razorpay API fails/is offline
            pass

    # Custom UPI Verification QR Code setup
    # Payment link text format for BHIM/GPay/PhonePe:
    # upi://pay?pa=bobbythecoder@upi&pn=BobbyTheCoder&am=GRAND_TOTAL&cu=INR
    upi_pa = settings.UPI_ID
    upi_pn = settings.UPI_MERCHANT_NAME
    upi_url = f"upi://pay?pa={upi_pa}&pn={urllib.parse.quote(upi_pn)}&am={grand_total}&cu=INR"
    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(upi_url)}"

    context = {
        'order': order,
        'products': products,
        'total_amount': total_amount,
        'discount_amount': discount_amount,
        'gst_amount': gst_amount,
        'grand_total': grand_total,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'upi_pa': upi_pa,
        'upi_pn': upi_pn,
        'qr_code_url': qr_code_url,
    }
    return render(request, 'shop/checkout.html', context)


@csrf_exempt
def payment_callback(request):
    # Handles Razorpay redirection / callback
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Verify Razorpay Signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            client.utility.verify_payment_signature(params_dict)
            
            order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id)
            order.status = 'completed'
            order.is_paid = True
            order.razorpay_payment_id = payment_id
            order.save()
            
            # Update coupon use counts
            if order.coupon:
                order.coupon.used_count += 1
                order.coupon.save()
                
            # Clear checkout session cart
            request.session['cart'] = {}
            request.session['applied_coupon'] = None
            
            # Email Invoice Alert
            send_mail(
                f"Order Confirmed: {order.order_id}",
                f"Hi {order.user.username},\n\nYour payment of ₹{order.grand_total} has been verified successfully. You can download your products in your User Dashboard.",
                settings.DEFAULT_FROM_EMAIL,
                [order.user.email],
                fail_silently=True
            )
            
            messages.success(request, "Payment successful! Your order has been placed.")
            return redirect('dashboard_overview')
        except Exception as e:
            messages.error(request, "Payment verification failed. If money was deducted, contact support.")
            return redirect('product_list')
            
    return redirect('product_list')


@login_required
def upi_verify_view(request):
    if request.method == "POST":
        order_id = request.POST.get('order_id')
        utr = request.POST.get('utr', '').strip()
        
        if not utr:
            messages.error(request, "Please enter a valid Transaction Ref / UTR number.")
            return redirect('checkout')
            
        order = get_object_or_404(Order, order_id=order_id, user=request.user)
        order.upi_verification_requested = True
        order.upi_utr = utr
        order.status = 'pending'
        order.save()
        
        # Clear checkout session cart
        request.session['cart'] = {}
        request.session['applied_coupon'] = None
        
        # Send Notification to Bobby (Admin)
        send_mail(
            "New UPI Payment Verification Pending",
            f"User {request.user.username} has submitted a manual UPI payment of ₹{order.grand_total}.\nOrder ID: {order.order_id}\nUTR Number: {utr}\nPlease verify this transaction in your Admin Dashboard.",
            settings.DEFAULT_FROM_EMAIL,
            ['bobby@bobbythecoder.in'],
            fail_silently=True
        )
        
        messages.success(request, "Your payment verification request has been submitted. It will be verified shortly.")
        return redirect('dashboard_overview')
        
    return redirect('product_list')
