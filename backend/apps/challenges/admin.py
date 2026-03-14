from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Challenge, Task


class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fields = ["day_number", "title", "is_completed"]
    readonly_fields = ["day_number"]


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "user_email",
        "goal_short",
        "status_badge",
        "duration_days",
        "progress_display",
        "created_at",
        "start_date",
    ]
    list_filter = [
        "status",
        "duration_days",
        "created_at",
        "start_date",
    ]
    search_fields = [
        "goal",
        "user__email",
        "user__display_name",
    ]
    readonly_fields = [
        "created_at",
        "progress_percentage",
        "detailed_progress",
    ]
    ordering = ["-created_at"]
    list_select_related = ["user"]
    inlines = [TaskInline]

    fieldsets = (
        (_("Challenge Information"), {"fields": ("user", "goal", "duration_days")}),
        (
            _("Status and Progress"),
            {
                "fields": (
                    "status",
                    "start_date",
                    "progress_percentage",
                    "detailed_progress",
                )
            },
        ),
        (
            _("Dates"),
            {
                "fields": ("created_at",),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="User", ordering="user__email")
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description="Goal")
    def goal_short(self, obj):
        return obj.goal[:50] + "..." if len(obj.goal) > 50 else obj.goal

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        colors = {
            "active": "#28a745",
            "completed": "#007bff",
            "abandoned": "#dc3545",
        }
        labels = {
            "active": "Active",
            "completed": "Completed",
            "abandoned": "Abandoned",
        }
        color = colors.get(obj.status, "#6c757d")
        label = labels.get(obj.status, obj.status)

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            label,
        )

    @admin.display(description="Progress")
    def progress_display(self, obj):
        percentage = obj.progress_percentage

        if percentage >= 80:
            color = "#28a745"
        elif percentage >= 50:
            color = "#ffc107"
        else:
            color = "#dc3545"

        return format_html(
            '<div style="width: 100px; background-color: #e9ecef; border-radius: 4px; overflow: hidden;">'
            '<div style="width: {}%; background-color: {}; padding: 2px 0; text-align: center; '
            'color: white; font-size: 11px; font-weight: bold;">{:.0f}%</div>'
            "</div>",
            percentage,
            color,
            percentage,
        )

    @admin.display(description="Detailed Progress")
    def detailed_progress(self, obj):
        tasks = obj.tasks.all()
        total = tasks.count()
        completed = tasks.filter(is_completed=True).count()
        percentage = obj.progress_percentage

        return format_html(
            '<div style="padding: 10px; background-color: #f8f9fa; border-radius: 5px;">'
            '<p style="margin: 0 0 10px 0;"><strong>Progress:</strong> {} of {} tasks completed ({:.1f}%)</p>'
            '<div style="width: 200px; height: 20px; background-color: #e9ecef; border-radius: 4px; overflow: hidden;">'
            '<div style="width: {}%; background-color: #28a745; height: 100%;"></div>'
            "</div>"
            "</div>",
            completed,
            total,
            percentage,
            percentage,
        )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "challenge_goal",
        "day_number",
        "title",
        "completion_badge",
    ]
    list_filter = [
        "is_completed",
        "day_number",
        "challenge__status",
    ]
    search_fields = [
        "title",
        "description",
        "challenge__goal",
        "challenge__user__email",
    ]
    readonly_fields = [
        "challenge",
        "day_number",
    ]
    ordering = ["challenge", "day_number"]
    list_select_related = ["challenge", "challenge__user"]

    fieldsets = (
        (
            _("Main Information"),
            {"fields": ("challenge", "day_number", "title", "description")},
        ),
        (_("Status"), {"fields": ("is_completed",)}),
    )

    @admin.display(description="Challenge", ordering="challenge__goal")
    def challenge_goal(self, obj):
        goal = obj.challenge.goal
        return goal[:40] + "..." if len(goal) > 40 else goal

    @admin.display(description="Status", ordering="is_completed")
    def completion_badge(self, obj):
        if obj.is_completed:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-weight: bold; font-size: 11px;">✓ Completed</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-weight: bold; font-size: 11px;">Not Completed</span>'
            )

    actions = ["mark_completed", "mark_not_completed"]

    @admin.action(description="✓ Mark as completed")
    def mark_completed(self, request, queryset):
        for task in queryset.select_related("challenge"):
            task.mark_completed()
        self.message_user(request, "Selected tasks marked as completed")

    @admin.action(description="✗ Mark as not completed")
    def mark_not_completed(self, request, queryset):
        for task in queryset.select_related("challenge"):
            task.mark_uncompleted()
        self.message_user(request, "Selected tasks marked as not completed")
