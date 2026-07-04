from django.contrib import admin
from .models import Project

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'technologies', 'live_url', 'github_url', 'created_at')
    search_fields = ('title', 'technologies', 'short_description')
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Project, ProjectAdmin)
