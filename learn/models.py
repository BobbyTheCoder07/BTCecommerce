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
    CONTENT_TYPE_CHOICES = [
        ('editor', 'Rich HTML Editor (CKEditor)'),
        ('code', 'Raw HTML Code'),
    ]

    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content_type = models.CharField(
        max_length=15, 
        choices=CONTENT_TYPE_CHOICES, 
        default='editor',
        help_text="Choose 'Rich HTML Editor' for normal text editing, or 'Raw HTML Code' to paste raw HTML."
    )
    content = models.TextField(blank=True, default="", help_text="Topic content in Rich HTML. Used if Rich HTML Editor is selected.")
    content_code = models.TextField(blank=True, default="", help_text="Topic content in Raw HTML. Used if Raw HTML Code is selected.")
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


class SubTopic(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='subtopics')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField(
        help_text="SubTopic content in HTML. Supports CKEditor rich editing and code blocks."
    )
    order = models.PositiveIntegerField(default=0, help_text="Display order within the parent topic")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.topic.title}-{self.title}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.topic.title} → {self.title}"
