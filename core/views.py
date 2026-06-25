from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db import IntegrityError

from django.db.models import Count
from .models import NewsletterSubscriber, ContactMessage, Service, Testimonial
from .forms import SignupForm, LoginForm, ContactForm
from shop.models import Product
from blog.models import Post
from projects.models import Project
from learn.models import Language

User = get_user_model()

class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch flagship product for hero promotion, and normal products
        context['flagship_product'] = Product.objects.filter(is_featured=True).first() or Product.objects.first()
        context['products'] = Product.objects.all()[:3]  # Showing top 3 ebooks
        context['recent_posts'] = Post.objects.order_by('-created_at')[:3]
        
        # New Dynamic Overhauls
        context['services'] = Service.objects.filter(is_active=True)[:3]
        context['projects'] = Project.objects.all()[:3]
        context['testimonials'] = Testimonial.objects.filter(is_active=True)
        context['languages'] = Language.objects.filter(is_active=True).annotate(topic_count=Count('topics'))[:3]
        
        # Total counts for stats badge
        context['total_ebooks'] = Product.objects.count()
        context['total_projects'] = Project.objects.count()
        context['total_languages'] = Language.objects.count()
        return context


class AboutView(TemplateView):
    template_name = 'core/about.html'


class ServicesView(TemplateView):
    template_name = 'core/services.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.filter(is_active=True)
        return context


class ContactView(TemplateView):
    template_name = 'core/contact.html'

    def get(self, request, *args, **kwargs):
        form = ContactForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true'

        if form.is_valid():
            contact_msg = ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message']
            )
            
            # Send message confirmation to owner & client
            send_mail(
                f"Contact Inquiry: {form.cleaned_data['subject']}",
                f"From: {form.cleaned_data['name']} ({form.cleaned_data['email']})\n\n{form.cleaned_data['message']}",
                'no-reply@bobbythecoder.in',
                ['bobby@bobbythecoder.in'],
                fail_silently=True
            )
            
            if is_ajax:
                return JsonResponse({
                    'status': 'success', 
                    'message': 'Your message has been sent successfully! Bobby will get back to you soon.'
                })
            
            messages.success(request, "Your message has been sent successfully! Bobby will get back to you soon.")
            return redirect('contact')
        
        if is_ajax:
            return JsonResponse({
                'status': 'error', 
                'errors': form.errors
            }, status=400)
            
        return render(request, self.template_name, {'form': form})


def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            return JsonResponse({'status': 'error', 'message': 'Please enter a valid email address.'})
        
        try:
            NewsletterSubscriber.objects.create(email=email)
            # Send confirmation
            send_mail(
                'Subscribed to BobbyTheCoder',
                'Thank you for subscribing to BobbyTheCoder! You will receive free coding notes and exclusive resources every week.',
                'no-reply@bobbythecoder.in',
                [email],
                fail_silently=True
            )
            return JsonResponse({'status': 'success', 'message': 'Thank you for subscribing! Keep an eye on your inbox.'})
        except IntegrityError:
            return JsonResponse({'status': 'info', 'message': 'You are already subscribed to our newsletter.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Something went wrong. Please try again.'})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])
            user.is_verified = False
            user.save()
            
            # Generate OTP & Send email
            otp = user.generate_otp()
            send_mail(
                'Verify your BobbyTheCoder Account',
                f'Welcome, {user.username}!\n\nYour OTP for account verification is: {otp}\nIt expires in 10 minutes.',
                'no-reply@bobbythecoder.in',
                [user.email],
                fail_silently=True
            )
            
            messages.info(request, "An OTP has been sent to your email. Please enter it below to verify your account.")
            return redirect('verify_otp', user_id=user.id)
    else:
        form = SignupForm()
    
    return render(request, 'core/signup.html', {'form': form})


def verify_otp_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_verified:
        return redirect('login')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        if user.verify_otp(entered_otp):
            messages.success(request, "Account verified successfully! You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Invalid or expired OTP. Please try again.")
            
    return render(request, 'core/verify_otp.html', {'user_id': user_id, 'user_email': user.email})


def resend_otp_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_verified:
        return redirect('login')
        
    otp = user.generate_otp()
    send_mail(
        'Verify your BobbyTheCoder Account',
        f'Your new OTP for account verification is: {otp}\nIt expires in 10 minutes.',
        'no-reply@bobbythecoder.in',
        [user.email],
        fail_silently=True
    )
    messages.success(request, "A new OTP has been sent to your email.")
    return redirect('verify_otp', user_id=user.id)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Allow login using email or username
            user = None
            if '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    username = user_obj.username
                except User.DoesNotExist:
                    username = username_or_email
            else:
                username = username_or_email

            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if not user.is_verified:
                    # Resend OTP
                    otp = user.generate_otp()
                    send_mail(
                        'Verify your BobbyTheCoder Account',
                        f'Please verify your account.\n\nYour OTP is: {otp}\nIt expires in 10 minutes.',
                        'no-reply@bobbythecoder.in',
                        [user.email],
                        fail_silently=True
                    )
                    messages.warning(request, "Your account is not verified yet. We have sent a new OTP to your email.")
                    return redirect('verify_otp', user_id=user.id)
                else:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.username}!")
                    return redirect('home')
            else:
                messages.error(request, "Invalid username/email or password.")
    else:
        form = LoginForm()
        
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        user = User.objects.filter(email=email).first()
        if user:
            # Send demo notification
            send_mail(
                'Password Reset Link (Demo)',
                f'Hi {user.username},\n\nThis is a mock password reset link. In a real environment, you would receive a tokens link.',
                'no-reply@bobbythecoder.in',
                [email],
                fail_silently=True
            )
        messages.info(request, "If an account exists with that email, we have sent a password reset link.")
        return redirect('login')
    return render(request, 'core/forgot_password.html')


def robots_txt_view(request):
    content = "User-agent: *\nDisallow: /admin/\nDisallow: /dashboard/\nSitemap: http://127.0.0.1:8000/sitemap.xml\n"
    return HttpResponse(content, content_type="text/plain")


def sitemap_xml_view(request):
    base_url = f"{request.scheme}://{request.get_host()}"
    urls = [
        "",
        "/about/",
        "/services/",
        "/contact/",
        "/blog/",
        "/shop/",
    ]
    
    # Dynamic database slugs
    from shop.models import Product
    from blog.models import Post
    
    for p in Product.objects.all():
        urls.append(f"/shop/product/{p.slug}/")
    for b in Post.objects.all():
        urls.append(f"/blog/{b.slug}/")

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    for url in urls:
        xml_lines.append("  <url>")
        xml_lines.append(f"    <loc>{base_url}{url}</loc>")
        xml_lines.append("    <changefreq>weekly</changefreq>")
        xml_lines.append("  </url>")
    xml_lines.append("</urlset>")
    
    return HttpResponse("\n".join(xml_lines), content_type="application/xml")

