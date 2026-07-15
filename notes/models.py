from django.db import models

class Note(models.Model):
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('django', 'Django'),
        ('html', 'HTML'),
        ('css', 'CSS'),
        ('javascript', 'JavaScript'),
        ('sql', 'SQL'),
        ('other', 'Other'),
    ]
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    programming_language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='other')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    thumbnail = models.ImageField(upload_to='notes/thumbnails/')
    CONTENT_TYPE_CHOICES = [
        ('markdown', 'Markdown / Code Editor'),
        ('html', 'Rich HTML Editor (CKEditor)'),
    ]
    content_type = models.CharField(
        max_length=15, 
        choices=CONTENT_TYPE_CHOICES, 
        default='markdown',
        help_text="Choose 'Markdown' for code blocks, or 'Rich HTML Editor' for normal text editing."
    )
    summary = models.TextField(help_text="Short abstract or quick-read notes preview.")
    content_markdown = models.TextField(blank=True, default="", help_text="Full notes text support Markdown syntax.")
    content_html = models.TextField(blank=True, default="", help_text="Rich HTML content. Used if Rich HTML Editor is selected.")
    pdf_file = models.FileField(upload_to='notes/pdfs/', blank=True, null=True, help_text="Upload premium offline notes PDF copy.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
