from django.db import models
from django.conf import settings

class Post(models.Model):
    CATEGORY_CHOICES = [
        ('coding_tips', 'Coding Tips'),
        ('career_advice', 'Career Advice'),
        ('python', 'Python'),
        ('django', 'Django'),
        ('web_dev', 'Web Development'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    thumbnail = models.ImageField(upload_to='blog/thumbnails/')
    content_markdown = models.TextField(help_text="Write blog post using markdown syntax.")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='web_dev')
    tags = models.CharField(max_length=200, help_text="Comma-separated tags e.g. django, server, security")
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def tag_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"
