from django.contrib import admin
from .models import Challenge, Task


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "goal_short",
        "status",
        "duration_days",
        "progress_percentage",
        "created_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = ["goal"]
    readonly_fields = ["created_at", "progress_percentage"]

    def goal_short(self, obj):
        return obj.goal[:50] + "..." if len(obj.goal) > 50 else obj.goal

    goal_short.short_description = "Цель"


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["id", "challenge", "day_number", "title", "is_completed"]
    list_filter = ["is_completed", "day_number"]
    search_fields = ["title", "description"]
