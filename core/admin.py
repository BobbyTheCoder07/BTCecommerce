from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, NewsletterSubscriber, ContactMessage, Service, Testimonial

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_verified', 'is_staff', 'is_active')
    list_filter = ('is_verified', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Verification Info', {'fields': ('is_verified', 'otp', 'otp_expiry')}),
    )

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'starting_price', 'order', 'is_active')
    list_editable = ('starting_price', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')

class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'rating', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('rating', 'is_active')
    search_fields = ('name', 'title', 'feedback')

admin.site.register(User, CustomUserAdmin)
admin.site.register(NewsletterSubscriber)
admin.site.register(ContactMessage)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Testimonial, TestimonialAdmin)
