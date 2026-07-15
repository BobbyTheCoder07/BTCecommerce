from django.contrib import admin
from .models import Language, Topic, SubTopic


class SubTopicInline(admin.StackedInline):
    model = SubTopic
    extra = 0
    prepopulated_fields = {'slug': ('title',)}
    fields = ('title', 'slug', 'content', 'order')

    class Media:
        js = (
            'https://cdn.ckeditor.com/ckeditor5/36.0.1/classic/ckeditor.js',
            'js/admin_ckeditor.js',
        )


class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'difficulty', 'order', 'created_at')
    list_filter = ('language', 'difficulty')
    search_fields = ('title', 'content', 'description')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {
            'fields': ('language', 'title', 'slug', 'difficulty', 'order')
        }),
        ('Description (Rich Editor)', {
            'fields': ('description',),
            'description': 'Short overview of this topic. CKEditor enabled.'
        }),
        ('Main Content (Rich Editor + Code)', {
            'fields': ('content',),
            'description': 'Full topic content. CKEditor enabled with code block support.'
        }),
    )
    inlines = [SubTopicInline]

    class Media:
        js = (
            'https://cdn.ckeditor.com/ckeditor5/36.0.1/classic/ckeditor.js',
            'js/admin_ckeditor.js',
        )


@admin.register(SubTopic)
class SubTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'order', 'created_at')
    list_filter = ('topic__language', 'topic')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}

    class Media:
        js = (
            'https://cdn.ckeditor.com/ckeditor5/36.0.1/classic/ckeditor.js',
            'js/admin_ckeditor.js',
        )


admin.site.register(Language)
admin.site.register(Topic, TopicAdmin)
