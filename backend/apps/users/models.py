import uuid
import secrets
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=150,
        unique=True,
        editable=False,
        blank=True,
    )
    display_name = models.CharField(
        max_length=150,
        blank=True,
        default="User",
        verbose_name="Display name",
    )
    language = models.CharField(
        max_length=5, choices=[("ru", "Русский"), ("en", "English")], default="en"
    )
    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def generate_username(self):
        return f"user_{uuid.uuid4().hex[:12]}"

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.generate_username()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class EmailVerification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_verifications",
    )
    old_email = models.EmailField()
    new_email = models.EmailField()
    code = models.CharField(max_length=6)
    confirm_token = models.UUIDField(default=uuid.uuid4, unique=True)
    cancel_token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = "".join([str(secrets.randbelow(10)) for _ in range(6)])
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)

    def is_valid(self):
        return (
            not self.is_used
            and not self.is_cancelled
            and timezone.now() < self.expires_at
        )

    def __str__(self):
        return f"{self.old_email} -> {self.new_email}"


class AccountDeletion(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account_deletions",
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def __str__(self):
        return f"AccountDeletion for {self.user.email}"


class PasswordResetCode(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_codes",
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    max_attempts = models.IntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = "".join([str(secrets.randbelow(10)) for _ in range(6)])
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def __str__(self):
        return f"PasswordReset for {self.user.email}"
