from django.db import models
from django.utils import timezone
from datetime import date
from django.contrib.auth import get_user_model
from .constants import (
    CHALLENGE_DURATION_DAYS,
    CHALLENGE_COLORS,
    STATUS_CHOICES,
    STATUS_ACTIVE,
)

User = get_user_model()


class Challenge(models.Model):
    """
    User's challenge model.
    
    Represents a 7-day challenge with AI-generated tasks.
    Tracks progress through current_day and completion status.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="challenges",
        null=False,
        blank=False,
        verbose_name="User",
    )
    goal = models.TextField(verbose_name="Goal")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    start_date = models.DateField(default=date.today, verbose_name="Start date")

    duration_days = models.IntegerField(
        default=CHALLENGE_DURATION_DAYS, verbose_name="Duration (days)"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        verbose_name="Status",
    )

    current_day = models.IntegerField(default=1, verbose_name="Current day")

    color = models.CharField(max_length=7, verbose_name="Color")

    class Meta:
        verbose_name = "Challenge"
        verbose_name_plural = "Challenges"
        ordering = ["-created_at"]
        indexes = [
                models.Index(fields=["user", "status"]),
                models.Index(fields=["user", "-created_at"]),
                models.Index(fields=["user", "status", "-created_at"]),
            ]

    def __str__(self):
        return f"Challenge: {self.goal[:50]}"

    def save(self, *args, **kwargs):
        if not self.pk and not self.color:
            user_challenges_count = Challenge.objects.filter(user=self.user).count()
            color_index = user_challenges_count % len(CHALLENGE_COLORS)
            self.color = CHALLENGE_COLORS[color_index]
        super().save(*args, **kwargs)

    @property
    def progress_percentage(self):
        """
        Calculate completion percentage based on completed tasks.

        Returns:
            int: Percentage from 0 to 100
        """
        total = self.tasks.count()
        if total == 0:
            return 0
        completed = self.tasks.filter(is_completed=True).count()
        return int((completed / total) * 100)


class Task(models.Model):
    """
    Individual task within a challenge.

    Each task belongs to a specific day and can be marked as completed.
    Tasks are ordered by day_number and order within each day.
    """

    challenge = models.ForeignKey(
        Challenge,
        related_name="tasks",
        on_delete=models.CASCADE,
        verbose_name="Challenge",
    )
    day_number = models.IntegerField(verbose_name="Day number")
    title = models.CharField(max_length=255, verbose_name="Title")
    description = models.TextField(verbose_name="Description")
    order = models.IntegerField(default=0, verbose_name="Order")
    is_completed = models.BooleanField(default=False, verbose_name="Is completed")
    completed_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Completed at"
    )

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ["day_number", "order"]
        indexes = [
                models.Index(fields=["challenge", "day_number"]),
                models.Index(fields=["challenge", "is_completed"]),
                models.Index(fields=["challenge", "day_number", "order"]), 
            ]

    def __str__(self):
        return f"Day {self.day_number}: {self.title}"

    def mark_completed(self):
        """
        Mark task as completed and advance challenge day if all day tasks are done.

        Idempotent - safe to call multiple times.
        """
        if self.is_completed:
            return

        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()

        challenge = self.challenge
        day_tasks = challenge.tasks.filter(day_number=self.day_number)
        completed_today = day_tasks.filter(is_completed=True).count()

        if completed_today == day_tasks.count():
            if challenge.current_day == self.day_number:
                challenge.current_day = self.day_number + 1
                challenge.save()

    def mark_uncompleted(self):
        if not self.is_completed:
            return

        self.is_completed = False
        self.completed_at = None
        self.save()

        challenge = self.challenge
        if challenge.current_day > self.day_number:
            current_day_tasks = challenge.tasks.filter(day_number=challenge.current_day)
            if current_day_tasks.exists() and not current_day_tasks.filter(is_completed=True).exists():
                challenge.current_day = self.day_number
                challenge.save()
