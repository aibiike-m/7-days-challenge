from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from axes.admin import AccessAttemptAdmin, AccessLogAdmin
from axes.models import AccessAttempt, AccessLog

from .models import CustomUser, EmailVerification, AccountDeletion, PasswordResetCode


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    list_display = [
        "email",
        "display_name",
        "language",
        "is_active",
        "is_staff",
        "date_joined",
        "last_login",
    ]
    list_filter = ["is_staff", "is_active", "language", "date_joined"]
    search_fields = ["email", "display_name", "username"]
    ordering = ["-date_joined"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("display_name", "language")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "display_name", "password1", "password2"),
            },
        ),
    )

    readonly_fields = ["date_joined", "last_login", "username"]


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):

    list_display = [
        "user",
        "old_email",
        "new_email",
        "code",
        "created_at",
        "expires_at",
        "is_used",
        "is_cancelled",
        "is_valid_status",
    ]
    list_filter = ["is_used", "is_cancelled", "created_at"]
    search_fields = ["user__email", "old_email", "new_email", "code"]
    readonly_fields = [
        "user",
        "old_email",
        "new_email",
        "code",
        "confirm_token",
        "cancel_token",
        "created_at",
        "expires_at",
    ]
    ordering = ["-created_at"]
    list_select_related = ["user"]

    @admin.display(boolean=True, description="Valid")
    def is_valid_status(self, obj):
        return obj.is_valid()


@admin.register(AccountDeletion)
class AccountDeletionAdmin(admin.ModelAdmin):

    list_display = [
        "user",
        "created_at",
        "expires_at",
        "is_used",
        "is_valid_status",
    ]
    list_filter = ["is_used", "created_at"]
    search_fields = ["user__email"]
    readonly_fields = ["user", "token", "created_at", "expires_at"]
    ordering = ["-created_at"]
    list_select_related = ["user"]

    @admin.display(boolean=True, description="Valid")
    def is_valid_status(self, obj):
        return obj.is_valid()


@admin.register(PasswordResetCode)
class PasswordResetCodeAdmin(admin.ModelAdmin):

    list_display = [
        "user",
        "code",
        "created_at",
        "expires_at",
        "is_used",
        "is_valid_status",
    ]
    list_filter = ["is_used", "created_at"]
    search_fields = ["user__email", "code"]
    readonly_fields = ["user", "code", "created_at", "expires_at"]
    ordering = ["-created_at"]
    list_select_related = ["user"]

    @admin.display(boolean=True, description="Valid")
    def is_valid_status(self, obj):
        return obj.is_valid()


admin.site.unregister(AccessAttempt)
admin.site.unregister(AccessLog)


@admin.register(AccessAttempt)
class CustomAccessAttemptAdmin(AccessAttemptAdmin):

    list_display = [
        "attempt_time",
        "ip_address",
        "username",
        "user_agent",
        "failures_since_start",
        "get_data",
    ]
    list_filter = ["attempt_time"]
    search_fields = ["username", "ip_address"]
    ordering = ["-attempt_time"]


@admin.register(AccessLog)
class CustomAccessLogAdmin(AccessLogAdmin):

    list_display = [
        "attempt_time",
        "ip_address",
        "username",
        "http_accept",
    ]
    list_filter = ["attempt_time"]
    search_fields = ["username", "ip_address"]
    ordering = ["-attempt_time"]
