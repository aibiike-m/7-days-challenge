from django.db import models
from django.utils import timezone
from datetime import date  


class Challenge(models.Model):
    goal = models.TextField(verbose_name="Цель")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    start_date = models.DateField(
        default=date.today, verbose_name="Дата начала" 
    )

    duration_days = models.IntegerField(default=7, verbose_name="Длительность")

    STATUS_CHOICES = [
        ("active", "Активный"),
        ("completed", "Завершенный"),
        ("abandoned", "Отмененный"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    class Meta:
        verbose_name = "Челлендж"
        verbose_name_plural = "Челленджи"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Челлендж: {self.goal[:50]}"

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
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()

    def mark_uncompleted(self):
        self.is_completed = False
        self.completed_at = None
        self.save()
