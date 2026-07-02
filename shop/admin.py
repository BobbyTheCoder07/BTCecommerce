from django.contrib import admin
from .models import Category, Product, Coupon, Order, OrderItem, Review, Wishlist

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ('product', 'price', 'quantity')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'price', 'discount_price', 'is_free', 'is_featured', 'created_at')
    list_filter = ('category', 'is_free', 'is_featured', 'programming_language', 'difficulty_level')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-created_at',)

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'discount_flat', 'is_active', 'expiry_date', 'usage_limit', 'used_count')
    list_filter = ('is_active', 'expiry_date')
    search_fields = ('code',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'total_amount', 'discount_amount', 'grand_total', 'status', 'is_paid', 'upi_verification_requested', 'created_at')
    list_filter = ('status', 'is_paid', 'upi_verification_requested', 'created_at')
    search_fields = ('order_id', 'razorpay_order_id', 'razorpay_payment_id', 'user__username', 'user__email', 'upi_utr')
    inlines = [OrderItemInline]
    ordering = ('-created_at',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('comment', 'product__title', 'user__username')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    search_fields = ('user__username', 'product__title')
