from django.contrib import admin
from .models import Note

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'programming_language', 'difficulty', 'created_at')
    list_filter = ('programming_language', 'difficulty', 'created_at')
    search_fields = ('title', 'summary', 'content_markdown', 'content_html')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-created_at',)
    fields = ('title', 'slug', 'programming_language', 'difficulty', 'thumbnail', 'pdf_file', 'content_type', 'summary', 'content_markdown', 'content_html')

    class Media:
        js = (
            'https://cdn.ckeditor.com/ckeditor5/36.0.1/classic/ckeditor.js',
            'js/admin_ckeditor.js',
            'js/admin_notes_toggle.js',
        )
