from django.db import transaction
from django.utils import translation
from ..models import Challenge, Task
from .ai_service import AIService


class ChallengeService:

    @staticmethod
    @transaction.atomic
    def create_challenge_with_tasks(
        goal: str, user, duration_days: int = 7, language: str = "ru"
    ) -> Challenge:
        ai_service = AIService()
        ai_data = ai_service.generate_challenge_plan(goal, duration_days)

        with translation.override("ru"):
            challenge = Challenge.objects.create(
                user=user,
                duration_days=duration_days,
                status="active",
                goal=ai_data.get("goal_ru", goal),
            )

        with translation.override("en"):
            challenge.goal = ai_data.get("goal_en", goal)
            challenge.save(update_fields=["goal"])

        for i, task_data in enumerate(ai_data["tasks"], start=1):
            with translation.override("ru"):
                task = Task.objects.create(
                    challenge=challenge,
                    day_number=task_data["day"],
                    title=task_data.get("title_ru", "Задача"),
                    description=task_data.get("description_ru", ""),
                    order=i,
                )

            title_en = task_data.get("title_en")
            description_en = task_data.get("description_en")
            if title_en or description_en:
                with translation.override("en"):
                    if title_en:
                        task.title = title_en
                    if description_en:
                        task.description = description_en
                    task.save(update_fields=["title", "description"])

        return challenge
    @staticmethod
    def get_active_challenge(user):
        """Get the user's last active challenge"""
        return (
            Challenge.objects.filter(user=user, status="active")
            .order_by("-created_at")
            .first()
        )
