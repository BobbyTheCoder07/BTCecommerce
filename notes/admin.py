from django.contrib import admin
from .models import Note

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'programming_language', 'difficulty', 'created_at')
    list_filter = ('programming_language', 'difficulty', 'created_at')
    search_fields = ('title', 'summary', 'content_markdown')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-created_at',)
