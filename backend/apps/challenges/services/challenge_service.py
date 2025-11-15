from django.db import transaction
from ..models import Challenge, Task
from .ai_service import AIService


class ChallengeService:
    """Сервис для работы с челленджами"""

    @staticmethod
    @transaction.atomic
    def create_challenge_with_tasks(
        goal: str, user, duration_days: int = 7
    ) -> Challenge:
        """
        Создает челлендж и генерирует задачи через AI

        Args:
            goal: Цель пользователя
            user: Пользователь (request.user)
            duration_days: Длительность в днях

        Returns:
            Challenge: Созданный челлендж с задачами
        """

        challenge = Challenge.objects.create(
            goal=goal,
            user=user,  
            duration_days=duration_days,
            status="active",
        )

        try:
            ai_service = AIService()
            tasks_data = ai_service.generate_challenge_plan(goal, duration_days)

            tasks_by_day = {}
            for task_data in tasks_data:
                day = task_data["day"]
                if day not in tasks_by_day:
                    tasks_by_day[day] = []
                tasks_by_day[day].append(task_data)

            tasks_to_create = []
            for day in sorted(tasks_by_day.keys()):
                for order, task_data in enumerate(tasks_by_day[day], start=1):
                    task = Task(
                        challenge=challenge,
                        day_number=task_data["day"],
                        title=task_data["title"],
                        description=task_data["description"],
                        order=order,
                    )
                    tasks_to_create.append(task)

            Task.objects.bulk_create(tasks_to_create)

            return challenge

        except Exception as e:
            challenge.delete()
            raise Exception(f"Не удалось создать челлендж: {str(e)}")

    @staticmethod
    def get_active_challenge(user):
        """Получить последний активный челлендж пользователя"""
        return (
            Challenge.objects.filter(user=user, status="active")
            .order_by("-created_at")
            .first()
        )
