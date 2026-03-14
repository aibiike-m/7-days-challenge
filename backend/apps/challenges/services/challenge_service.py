from django.db import transaction
from django.utils import translation
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
import logging

from ..models import Challenge, Task
from .ai_service import AIService

logger = logging.getLogger(__name__)


class ChallengeService:
    MAX_ACTIVE_CHALLENGES = getattr(settings, "MAX_ACTIVE_CHALLENGES", 10)
    MAX_CHALLENGES_PER_DAY = getattr(settings, "MAX_CHALLENGES_PER_DAY", 15)

    @staticmethod
    @transaction.atomic
    def create_challenge_with_tasks(
        goal: str, user, duration_days: int = 7, language: str = "ru"
    ) -> Challenge:

        active_count = Challenge.objects.filter(user=user, status="active").count()
        if active_count >= ChallengeService.MAX_ACTIVE_CHALLENGES:
            logger.warning(
                f"Active challenges limit exceeded: user={user.email}, "
                f"active={active_count}, limit={ChallengeService.MAX_ACTIVE_CHALLENGES}"
            )
            raise ValidationError(
                f"You cannot have more than {ChallengeService.MAX_ACTIVE_CHALLENGES} active challenges. "
                f"Please complete or delete some challenges first."
            )

        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        created_today = Challenge.objects.filter(
            user=user, created_at__gte=today_start
        ).count()
        if created_today >= ChallengeService.MAX_CHALLENGES_PER_DAY:
            logger.warning(
                f"Daily creation limit exceeded: user={user.email}, "
                f"created_today={created_today}, limit={ChallengeService.MAX_CHALLENGES_PER_DAY}"
            )
            raise ValidationError(
                f"Daily limit reached ({ChallengeService.MAX_CHALLENGES_PER_DAY}). "
                f"Please try again tomorrow."
            )

        if not goal or len(goal.strip()) < 10:
            raise ValidationError("Goal must be at least 10 characters long.")

        if len(goal) > 500:
            raise ValidationError("Goal is too long. Maximum 500 characters allowed.")

        logger.info(
            f"Creating challenge: user={user.email}, "
            f"active_count={active_count}, created_today={created_today}, "
            f"goal_length={len(goal)}"
        )

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

        logger.info(
            f"Challenge created successfully: user={user.email}, "
            f"challenge_id={challenge.id}, tasks_count={len(ai_data['tasks'])}"
        )

        return challenge

    @staticmethod
    def get_active_challenge(user):
        """Get the user's last active challenge"""
        return (
            Challenge.objects.filter(user=user, status="active")
            .order_by("-created_at", "-id")
            .first()
        )

    @staticmethod
    def get_user_stats(user) -> dict:
        """
        Get user's challenge statistics for monitoring.

        Returns:
            dict: Statistics including active count, today count, limits
        """
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        active_count = Challenge.objects.filter(user=user, status="active").count()

        created_today = Challenge.objects.filter(
            user=user, created_at__gte=today_start
        ).count()

        return {
            "active_challenges": active_count,
            "max_active": ChallengeService.MAX_ACTIVE_CHALLENGES,
            "can_create_active": active_count < ChallengeService.MAX_ACTIVE_CHALLENGES,
            "created_today": created_today,
            "max_per_day": ChallengeService.MAX_CHALLENGES_PER_DAY,
            "can_create_today": created_today < ChallengeService.MAX_CHALLENGES_PER_DAY,
            "remaining_today": max(
                0, ChallengeService.MAX_CHALLENGES_PER_DAY - created_today
            ),
        }
