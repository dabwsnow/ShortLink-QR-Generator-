from django.contrib import admin
from .models import Link


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "original_url", "clicks", "created_at")
    search_fields = ("code", "title", "original_url")
    list_filter = ("created_at",)
    readonly_fields = ("clicks", "created_at", "last_accessed")
