from django.db import models
from django.utils.text import slugify

class Project(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    thumbnail = models.ImageField(upload_to='projects/thumbnails/')
    technologies = models.CharField(max_length=200, help_text="Comma-separated values e.g. Django, Python, PostgreSQL, GSAP")
    short_description = models.TextField()
    description = models.TextField(blank=True, null=True, help_text="Full detail case study content. Supports HTML.")
    live_url = models.URLField(blank=True, null=True, help_text="Link to live hosted website.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def tech_list(self):
        return [t.strip() for t in self.technologies.split(',') if t.strip()]

    def __str__(self):
        return self.title
