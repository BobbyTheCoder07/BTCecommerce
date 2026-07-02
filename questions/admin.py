from django.contrib import admin
from .models import Question

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'difficulty', 'category', 'created_at')
    list_filter = ('difficulty', 'category', 'created_at')
    search_fields = ('title', 'problem_statement', 'explanation')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-created_at',)
