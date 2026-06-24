from django.contrib import admin
from .models import Language, Topic

class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'difficulty', 'order')
    list_filter = ('language', 'difficulty')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    
    class Media:
        js = (
            'https://cdn.ckeditor.com/ckeditor5/36.0.1/classic/ckeditor.js',
            'js/admin_ckeditor.js',
        )

admin.site.register(Language)
admin.site.register(Topic, TopicAdmin)
