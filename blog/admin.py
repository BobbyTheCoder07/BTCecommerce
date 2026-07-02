from django.contrib import admin
from .models import Post, Comment

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('user', 'created_at')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'views', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content_markdown')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CommentInline]
    ordering = ('-created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'post__title', 'user__username')
