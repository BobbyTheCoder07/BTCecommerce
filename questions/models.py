from django.db import models

class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    CATEGORY_CHOICES = [
        ('python', 'Python Questions'),
        ('django', 'Django Questions'),
        ('frontend', 'Frontend Questions'),
        ('interview', 'Interview Questions'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='python')
    tags = models.CharField(max_length=200, help_text="Comma-separated values e.g. loops, dynamic-programming")
    problem_statement = models.TextField()
    explanation = models.TextField(help_text="Detailed step-by-step logic breakdown.")
    solution_code = models.TextField(help_text="Solution in Programming Language syntax.")
    sample_output = models.TextField(blank=True, null=True, help_text="Console output resulting from executing the code.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def tag_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
