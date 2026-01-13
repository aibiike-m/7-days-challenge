from django.db import models
from django.utils import timezone
from datetime import date  
from django.contrib.auth import get_user_model
from .constants import CHALLENGE_DURATION_DAYS


User = get_user_model()

class Challenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="challenges", null=False, blank=False)
    goal = models.TextField(verbose_name="Цель")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    start_date = models.DateField(
        default=date.today, verbose_name="Дата начала" 
    )

    duration_days = models.IntegerField(
        default=CHALLENGE_DURATION_DAYS, verbose_name="Длительность"
    )

    STATUS_CHOICES = [
        ("active", "Активный"),
        ("completed", "Завершенный"),
        ("abandoned", "Отмененный"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    current_day = models.IntegerField(
        default=1,
        verbose_name="Текущий день",
    )

    color = models.CharField(
        max_length=7, 
        verbose_name="Цвет"
    )

    COLORS = [
        "#F4A7B9",  # Cherry Blossom (Soft Pink)
        "#E0B2C8",  # Orchid Petal (Muted Pink/Purple)
        "#A7E6D8",  # Aquamarine (Bright Mint)
        "#B6EB6E",  # Lime Sorbet (Fresh Light Green)
        "#479FC8",  # Ocean Blue (Clear Blue)
        "#B58FEB",  # Bright Lavender (Soft Violet)
        "#FF8080",  # Coral Red (Warm Salmon)
        "#F72F57",  # Deep Rose (Vibrant Pink/Red)
        "#8FECF7",  # Electric Ice (Bright Cyan)
        "#EDCB5A",  # Golden Sand (Warm Mustard/Yellow)
    ]

    class Meta:
        verbose_name = "Челлендж"
        verbose_name_plural = "Челленджи"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Челлендж: {self.goal[:50]}"

    def save(self, *args, **kwargs):
        if not self.pk and not self.color:
            user_challenges_count = Challenge.objects.filter(user=self.user).count()
            color_index = user_challenges_count % len(self.COLORS)
            self.color = self.COLORS[color_index]
        super().save(*args, **kwargs)

    @property
    def progress_percentage(self):
        total = self.tasks.count()
        if total == 0:
            return 0
        completed = self.tasks.filter(is_completed=True).count()
        return int((completed / total) * 100)


class Task(models.Model):
    challenge = models.ForeignKey(
        Challenge,
        related_name="tasks",
        on_delete=models.CASCADE,
        verbose_name="Челлендж",
    )
    day_number = models.IntegerField(verbose_name="День №")
    title = models.CharField(max_length=255, verbose_name="Название") 
    description = models.TextField(verbose_name="Описание")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    is_completed = models.BooleanField(default=False, verbose_name="Выполнена")
    completed_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата выполнения"
    )

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["day_number", "order"]

    def __str__(self):
        return f"День {self.day_number}: {self.title}"

    def mark_completed(self):
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
            if not current_day_tasks.filter(is_completed=True).exists():
                challenge.current_day = self.day_number
                challenge.save()
