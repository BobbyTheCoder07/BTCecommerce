from django.contrib import admin
from .models import Language, Topic, SubTopic


class SubTopicInline(admin.StackedInline):
    model = SubTopic
    extra = 0
    prepopulated_fields = {'slug': ('title',)}
    fields = ('title', 'slug', 'content_type', 'content', 'content_code', 'order')

    class Media:
        js = (
            'https://cdn.ckeditor.com/ckeditor5/36.0.1/classic/ckeditor.js',
            'js/admin_ckeditor.js',
            'js/admin_learn_toggle.js',
        )


class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'difficulty', 'order', 'created_at')
    list_filter = ('language', 'difficulty')
    search_fields = ('title', 'content', 'content_code')
    prepopulated_fields = {'slug': ('title',)}
    fields = ('language', 'title', 'slug', 'difficulty', 'order', 'content_type', 'content', 'content_code')
    inlines = [SubTopicInline]

    class Media:
        js = (
            'https://cdn.ckeditor.com/ckeditor5/36.0.1/classic/ckeditor.js',
            'js/admin_ckeditor.js',
            'js/admin_learn_toggle.js',
        )


@admin.register(SubTopic)
class SubTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'order', 'created_at')
    list_filter = ('topic__language', 'topic')
    search_fields = ('title', 'content', 'content_code')
    prepopulated_fields = {'slug': ('title',)}
    fields = ('topic', 'title', 'slug', 'content_type', 'content', 'content_code', 'order')

    class Media:
        js = (
            'https://cdn.ckeditor.com/ckeditor5/36.0.1/classic/ckeditor.js',
            'js/admin_ckeditor.js',
            'js/admin_learn_toggle.js',
        )


admin.site.register(Language)
admin.site.register(Topic, TopicAdmin)
