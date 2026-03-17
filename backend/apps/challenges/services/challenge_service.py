from django.conf import settings
from django.db import transaction
from django.utils import translation
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import logging

from ..models import Challenge, Task
from .ai_service import AIService
from ..constants import (
    CHALLENGE_DURATION_DAYS,
    STATUS_ACTIVE,
    MIN_GOAL_LENGTH,
    MAX_GOAL_LENGTH,
)

logger = logging.getLogger(__name__)


class ChallengeService:

    @staticmethod
    def _get_active_challenges_count(user) -> int:
        today = timezone.now().date()
        active_limit_date = today - timedelta(days=CHALLENGE_DURATION_DAYS)
        return Challenge.objects.filter(
            user=user,
            status=STATUS_ACTIVE,
            start_date__gt=active_limit_date,
        ).count()

    @staticmethod
    @transaction.atomic
    def create_challenge_with_tasks(
        goal: str,
        user,
        duration_days: int = CHALLENGE_DURATION_DAYS,
        language: str = "ru",
    ) -> Challenge:

        active_count = ChallengeService._get_active_challenges_count(user)
        if active_count >= settings.MAX_ACTIVE_CHALLENGES:
            logger.warning(
                f"Active challenges limit exceeded: user={user.email}, "
                f"active={active_count}, limit={settings.MAX_ACTIVE_CHALLENGES}"
            )
            raise ValidationError("max_challenges_exceeded")

        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        created_today = Challenge.objects.filter(
            user=user, created_at__gte=today_start
        ).count()
        if created_today >= settings.MAX_CHALLENGES_PER_DAY:
            logger.warning(
                f"Daily creation limit exceeded: user={user.email}, "
                f"created_today={created_today}, limit={settings.MAX_CHALLENGES_PER_DAY}"
            )
            raise ValidationError("daily_limit_exceeded")

        if not goal or len(goal.strip()) < MIN_GOAL_LENGTH:
            raise ValidationError("goal_too_short")

        if len(goal) > MAX_GOAL_LENGTH:
            raise ValidationError("goal_too_long")

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
                status=STATUS_ACTIVE,
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
        today = timezone.now().date()
        active_limit_date = today - timedelta(days=CHALLENGE_DURATION_DAYS)
        return (
            Challenge.objects.filter(
                user=user,
                status=STATUS_ACTIVE,
                start_date__gt=active_limit_date,
            )
            .order_by("-created_at", "-id")
            .first()
        )

    @staticmethod
    def get_user_stats(user) -> dict:
        """Get user's challenge statistics for monitoring."""
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        active_count = ChallengeService._get_active_challenges_count(user)

        created_today = Challenge.objects.filter(
            user=user, created_at__gte=today_start
        ).count()

        return {
            "active_challenges": active_count,
            "max_active": settings.MAX_ACTIVE_CHALLENGES,
            "can_create_active": active_count < settings.MAX_ACTIVE_CHALLENGES,
            "created_today": created_today,
            "max_per_day": settings.MAX_CHALLENGES_PER_DAY,
            "can_create_today": created_today < settings.MAX_CHALLENGES_PER_DAY,
            "remaining_today": max(0, settings.MAX_CHALLENGES_PER_DAY - created_today),
        }
