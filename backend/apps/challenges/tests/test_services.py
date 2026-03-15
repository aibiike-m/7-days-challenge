import pytest
import json
from unittest.mock import patch, MagicMock, PropertyMock
from google.generativeai.types import GenerateContentResponse

from apps.challenges.models import Challenge, Task
from apps.challenges.services.challenge_service import ChallengeService
from apps.challenges.services.ai_service import AIService
from apps.challenges.constants import (
    STATUS_ACTIVE,
    STATUS_COMPLETED,
    CHALLENGE_DURATION_DAYS,
    ERROR_AI_INVALID_JSON,
    ERROR_AI_INVALID_FORMAT,
)


@pytest.mark.django_db
class TestChallengeService:
    @patch("apps.challenges.services.ai_service.genai.GenerativeModel")
    def test_create_challenge_with_tasks_success(
        self, mock_model, user, mock_ai_response
    ):
        from django.utils import translation

        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_ai_response)
        mock_model.return_value.generate_content.return_value = mock_response

        challenge = ChallengeService.create_challenge_with_tasks(
            goal="Learn Python", user=user, language="ru"
        )

        assert challenge is not None
        assert challenge.user == user

        with translation.override("ru"):
            challenge.refresh_from_db()
            assert challenge.goal == "Выучить Python за 7 дней"

        with translation.override("en"):
            challenge.refresh_from_db()
            assert challenge.goal == "Learn Python in 7 days"

        assert challenge.status == STATUS_ACTIVE
        assert challenge.duration_days == CHALLENGE_DURATION_DAYS

        tasks = challenge.tasks.all()
        assert tasks.count() == len(mock_ai_response["tasks"])

        first_task = tasks.first()
        assert first_task.day_number == 1

        with translation.override("ru"):
            first_task.refresh_from_db()
            assert first_task.title == "Установка Python"

        assert first_task.order == 1

    @patch("apps.challenges.services.ai_service.genai.GenerativeModel")
    def test_create_challenge_with_english_language(
        self, mock_model, user, mock_ai_response
    ):
        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_ai_response)
        mock_model.return_value.generate_content.return_value = mock_response

        challenge = ChallengeService.create_challenge_with_tasks(
            goal="Learn Python", user=user, language="en"
        )

        assert challenge.goal
        tasks = challenge.tasks.all()
        assert tasks.count() > 0

    @patch("apps.challenges.services.ai_service.genai.GenerativeModel")
    def test_create_challenge_with_minimal_tasks(
        self, mock_model, user, minimal_ai_response
    ):
        mock_response = MagicMock()
        mock_response.text = json.dumps(minimal_ai_response)
        mock_model.return_value.generate_content.return_value = mock_response

        challenge = ChallengeService.create_challenge_with_tasks(
            goal="A long goal for testing purposes",
            user=user,
            language="ru",
        )

        assert challenge.tasks.count() == 1

    @patch("apps.challenges.services.ai_service.genai.GenerativeModel")
    def test_create_challenge_tasks_have_correct_order(
        self, mock_model, user, mock_ai_response
    ):
        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_ai_response)
        mock_model.return_value.generate_content.return_value = mock_response

        challenge = ChallengeService.create_challenge_with_tasks(
            goal="Learn Python", user=user, language="ru"
        )

        tasks = challenge.tasks.all().order_by("order")

        for i, task in enumerate(tasks, start=1):
            assert task.order == i

    @patch("apps.challenges.services.ai_service.genai.GenerativeModel")
    def test_create_challenge_handles_missing_translations(self, mock_model, user):
        incomplete_response = {
            "goal_ru": "Длинная цель на русском для тестирования",
            "tasks": [
                {
                    "day": 1,
                    "title_ru": "Задача",
                    "description_ru": "Описание",
                }
            ],
        }

        mock_response = MagicMock()
        mock_response.text = json.dumps(incomplete_response)
        mock_model.return_value.generate_content.return_value = mock_response

        challenge = ChallengeService.create_challenge_with_tasks(
            goal="Learn how to play guitar in seven days with practice", 
            user=user, 
            language="ru"
        )

        assert challenge.tasks.count() == 1

    def test_get_active_challenge(self, user):
        from datetime import timedelta
        from django.utils import timezone

        now = timezone.now()

        old_challenge = Challenge.objects.create(
            user=user, goal="Old", status=STATUS_ACTIVE
        )
        old_challenge.created_at = now - timedelta(seconds=2)
        old_challenge.save()

        expected = Challenge.objects.create(user=user, goal="New", status=STATUS_ACTIVE)
        expected.created_at = now - timedelta(seconds=1)
        expected.save()

        completed = Challenge.objects.create(
            user=user, goal="Completed", status=STATUS_COMPLETED
        )
        completed.created_at = now
        completed.save()

        result = ChallengeService.get_active_challenge(user)

        assert result == expected

    def test_get_active_challenge_returns_none_when_no_active(self, user):
        Challenge.objects.create(user=user, goal="Completed", status=STATUS_COMPLETED)

        result = ChallengeService.get_active_challenge(user)

        assert result is None

    def test_get_active_challenge_returns_none_when_empty(self, user):
        result = ChallengeService.get_active_challenge(user)
        assert result is None


@pytest.mark.django_db
class TestAIService:
    @patch("apps.challenges.services.ai_service.genai.GenerativeModel")
    def test_generate_challenge_plan_success(self, mock_model, mock_ai_response):
        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_ai_response)
        mock_model.return_value.generate_content.return_value = mock_response

        service = AIService()
        result = service.generate_challenge_plan("Learn Python", days=7)

        assert result == mock_ai_response
        assert "tasks" in result
        assert "goal_ru" in result
        assert "goal_en" in result

    @patch("apps.challenges.services.ai_service.genai.GenerativeModel")
    def test_generate_challenge_plan_strips_markdown(
        self, mock_model, mock_ai_response
    ):
        markdown_response = f"```json\n{json.dumps(mock_ai_response)}\n```"

        mock_response = MagicMock()
        mock_response.text = markdown_response
        mock_model.return_value.generate_content.return_value = mock_response

        service = AIService()
        result = service.generate_challenge_plan("Learn Python")

        assert result == mock_ai_response

    @patch("apps.challenges.services.ai_service.genai.GenerativeModel")
    def test_generate_challenge_plan_invalid_json_raises_error(self, mock_model):
        mock_response = MagicMock()
        mock_response.text = "This is not JSON"
        mock_model.return_value.generate_content.return_value = mock_response

        service = AIService()

        with pytest.raises(Exception) as exc_info:
            service.generate_challenge_plan("Test goal")

        assert ERROR_AI_INVALID_JSON in str(exc_info.value)

    @patch("apps.challenges.services.ai_service.genai.GenerativeModel")
    def test_generate_challenge_plan_missing_tasks_key_raises_error(self, mock_model):
        invalid_response = {"goal_ru": "Test", "goal_en": "Test"}

        mock_response = MagicMock()
        mock_response.text = json.dumps(invalid_response)
        mock_model.return_value.generate_content.return_value = mock_response

        service = AIService()

        with pytest.raises(Exception) as exc_info:
            service.generate_challenge_plan("Test goal")

        assert ERROR_AI_INVALID_FORMAT in str(exc_info.value)

    @patch("apps.challenges.services.ai_service.genai.GenerativeModel")
    @patch(
        "apps.challenges.services.ai_service.time.sleep"
    )
    def test_generate_challenge_plan_retries_on_failure(
        self, mock_sleep, mock_model, mock_ai_response
    ):
        mock_response_fail = MagicMock()
        mock_response_fail.text = "invalid json"

        mock_response_success = MagicMock()
        mock_response_success.text = json.dumps(mock_ai_response)

        mock_model.return_value.generate_content.side_effect = [
            mock_response_fail,
            mock_response_success,
        ]

        service = AIService()
        result = service.generate_challenge_plan("Test goal")

        assert result == mock_ai_response

        assert mock_model.return_value.generate_content.call_count == 2

        assert mock_sleep.called

    @patch("apps.challenges.services.ai_service.genai.GenerativeModel")
    @patch("apps.challenges.services.ai_service.time.sleep")
    def test_generate_challenge_plan_fails_after_max_retries(
        self, mock_sleep, mock_model
    ):
        mock_response = MagicMock()
        mock_response.text = "invalid json"
        mock_model.return_value.generate_content.return_value = mock_response

        service = AIService()

        with pytest.raises(Exception):
            service.generate_challenge_plan("Test goal")

        assert mock_model.return_value.generate_content.call_count == 3

    @patch("apps.challenges.services.ai_service.genai.GenerativeModel")
    def test_generate_challenge_plan_handles_no_response_text(self, mock_model):
        mock_response = MagicMock()
        del mock_response.text
        mock_model.return_value.generate_content.return_value = mock_response

        service = AIService()

        with pytest.raises(Exception):
            service.generate_challenge_plan("Test goal")

    @patch("apps.challenges.services.ai_service.genai.GenerativeModel")
    def test_generate_challenge_plan_custom_days(self, mock_model, mock_ai_response):
        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_ai_response)
        mock_model.return_value.generate_content.return_value = mock_response

        service = AIService()
        result = service.generate_challenge_plan("Test goal", days=14)

        assert mock_model.return_value.generate_content.called

        call_args = mock_model.return_value.generate_content.call_args
        prompt = call_args[0][0]

        assert "14" in prompt


@pytest.mark.django_db
class TestServiceIntegration:
    @patch("apps.challenges.services.ai_service.genai.GenerativeModel")
    def test_full_challenge_creation_flow(self, mock_model, user, mock_ai_response):
        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_ai_response)
        mock_model.return_value.generate_content.return_value = mock_response

        challenge = ChallengeService.create_challenge_with_tasks(
            goal="Learn Python in 7 days", user=user, language="en"
        )

        assert Challenge.objects.filter(user=user).count() == 1
        assert Task.objects.filter(challenge=challenge).count() == len(
            mock_ai_response["tasks"]
        )

        for task in challenge.tasks.all():
            assert task.challenge == challenge
            assert task.day_number >= 1
            assert task.day_number <= 7

    @patch("apps.challenges.services.ai_service.genai.GenerativeModel")
    def test_multiple_challenges_different_colors(
        self, mock_model, user, minimal_ai_response
    ):
        mock_response = MagicMock()
        mock_response.text = json.dumps(minimal_ai_response)
        mock_model.return_value.generate_content.return_value = mock_response

        challenges = []
        for i in range(3):
            challenge = ChallengeService.create_challenge_with_tasks(
                goal=f"This is a long test goal for challenge number {i}",
                 user=user,
                language="en",
            )
            challenges.append(challenge)

        colors = [c.color for c in challenges]
        assert len(colors) == len(set(colors))
