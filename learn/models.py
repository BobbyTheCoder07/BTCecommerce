from django.db import models
from django.utils.text import slugify

class Language(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=100, help_text="FontAwesome class e.g. fa-brands fa-python")
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='languages/thumbnails/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Topic(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField(help_text="Topic content in HTML. Will render with |safe.")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    order = models.PositiveIntegerField(default=0, help_text="Custom order rank in sidebar")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.language.name}-{self.title}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.language.name} - {self.title}"
