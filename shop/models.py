from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('django', 'Django'),
        ('html_css', 'HTML & CSS'),
        ('javascript', 'JavaScript'),
        ('mysql', 'MySQL'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    thumbnail = models.ImageField(upload_to='products/thumbnails/')
    is_free = models.BooleanField(default=False)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    programming_language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='other')
    file = models.FileField(upload_to='products/files/', blank=True, null=True)  # Digital Product Delivery
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def current_price(self):
        if self.is_free:
            return 0.00
        if self.discount_price:
            return self.discount_price
        return self.price

    @property
    def has_discount(self):
        return not self.is_free and self.discount_price is not None and self.discount_price < self.price


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(100)])
    discount_flat = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    expiry_date = models.DateField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='exclusive_coupons')  # User specific coupons

    def __str__(self):
        return self.code

    def is_valid(self, user=None):
        if not self.is_active:
            return False, "This coupon is inactive."
        if self.expiry_date and self.expiry_date < timezone.now().date():
            return False, "This coupon has expired."
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False, "This coupon has reached its usage limit."
        if self.users.exists() and (user is None or not self.users.filter(id=user.id).exists()):
            return False, "This coupon is not valid for your account."
        return True, "Coupon applied successfully!"

    def calculate_discount(self, amount):
        if self.discount_percentage:
            return (amount * self.discount_percentage) / 100
        if self.discount_flat:
            return min(self.discount_flat, amount)
        return 0


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    order_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Price before coupon
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # GST Ready
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)  # Total to be paid
    
    is_paid = models.BooleanField(default=False)
    
    # UPI Offline Payment Verification
    upi_verification_requested = models.BooleanField(default=False)
    upi_utr = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} on {self.product.title}"


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username}'s wishlist item: {self.product.title}"
