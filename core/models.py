from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import random

class User(AbstractUser):
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)

    def generate_otp(self):
        self.otp = f"{random.randint(100000, 999999)}"
        self.otp_expiry = timezone.now() + timezone.timedelta(minutes=10)
        self.save()
        return self.otp

    def verify_otp(self, entered_otp):
        if self.otp and self.otp == entered_otp and self.otp_expiry and timezone.now() < self.otp_expiry:
            self.is_verified = True
            self.otp = None
            self.otp_expiry = None
            self.save()
            return True
        return False


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"


class Service(models.Model):
    icon = models.CharField(max_length=100, help_text="FontAwesome icon class name e.g. fa-solid fa-code")
    title = models.CharField(max_length=100)
    description = models.TextField()
    starting_price = models.CharField(max_length=50, help_text="e.g. ₹15,000 or ₹79/hr")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, help_text="Client role or company e.g. CTO at Startup")
    image = models.ImageField(upload_to='testimonials/profiles/', blank=True, null=True)
    rating = models.PositiveIntegerField(default=5)
    feedback = models.TextField()
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} ({self.title})"

