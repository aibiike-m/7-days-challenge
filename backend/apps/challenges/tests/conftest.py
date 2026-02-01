import pytest
from datetime import timedelta
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.challenges.models import Challenge, Task
from apps.challenges.constants import (
    CHALLENGE_DURATION_DAYS,
    STATUS_ACTIVE,
    STATUS_COMPLETED,
)

User = get_user_model()


# ==================== CLIENT FIXTURES ====================


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="test@example.com", password="testpass123", language="en"
    )


@pytest.fixture
def russian_user(db):
    return User.objects.create_user(
        email="russian@example.com", password="testpass123", language="ru"
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(email="other@example.com", password="testpass123")


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


# ==================== MODEL FIXTURES ====================


@pytest.fixture
def challenge(user):
    return Challenge.objects.create(
        user=user,
        goal="Learn Python",
        status=STATUS_ACTIVE,
        duration_days=CHALLENGE_DURATION_DAYS,
    )


@pytest.fixture
def completed_challenge(user):
    return Challenge.objects.create(
        user=user,
        goal="Completed challenge",
        status=STATUS_COMPLETED,
        duration_days=CHALLENGE_DURATION_DAYS,
    )


@pytest.fixture
def old_challenge(user):
    challenge = Challenge.objects.create(
        user=user,
        goal="Old challenge",
        status=STATUS_ACTIVE,
    )
    challenge.created_at = challenge.created_at - timedelta(days=7)
    challenge.save()
    return challenge


@pytest.fixture
def task(challenge):
    return Task.objects.create(
        challenge=challenge,
        day_number=1,
        title="Setup environment",
        description="Install Python and VSCode",
        order=1,
    )


@pytest.fixture
def completed_task(challenge):
    task = Task.objects.create(
        challenge=challenge,
        day_number=1,
        title="Completed task",
        description="Test description",
        order=1,
    )
    task.mark_completed()
    return task


@pytest.fixture
def future_task(challenge):
    return Task.objects.create(
        challenge=challenge,
        day_number=10,
        title="Future task",
        description="This task is in the future",
        order=1,
    )


@pytest.fixture
def multiple_tasks(challenge):
    tasks = []
    for i in range(1, 4):
        task = Task.objects.create(
            challenge=challenge,
            day_number=1,
            title=f"Task {i}",
            description=f"Description {i}",
            order=i,
        )
        tasks.append(task)
    return tasks


# ==================== AI MOCK DATA ====================


@pytest.fixture
def mock_ai_response():
    return {
        "goal_ru": "Выучить Python за 7 дней",
        "goal_en": "Learn Python in 7 days",
        "tasks": [
            {
                "day": 1,
                "title_ru": "Установка Python",
                "title_en": "Install Python",
                "description_ru": "Скачайте и установите Python 3.11+",
                "description_en": "Download and install Python 3.11+",
            },
            {
                "day": 1,
                "title_ru": "Настройка IDE",
                "title_en": "Setup IDE",
                "description_ru": "Установите VS Code или PyCharm",
                "description_en": "Install VS Code or PyCharm",
            },
            {
                "day": 2,
                "title_ru": "Изучение основ",
                "title_en": "Learn basics",
                "description_ru": "Переменные, типы данных, операторы",
                "description_en": "Variables, data types, operators",
            },
            {
                "day": 3,
                "title_ru": "Функции",
                "title_en": "Functions",
                "description_ru": "Создание и использование функций",
                "description_en": "Creating and using functions",
            },
        ],
    }


@pytest.fixture
def invalid_ai_response():
    return "```json\n{invalid json}\n```"


@pytest.fixture
def minimal_ai_response():
    return {
        "goal_ru": "Тест",
        "goal_en": "Test",
        "tasks": [
            {
                "day": 1,
                "title_ru": "Задача",
                "title_en": "Task",
                "description_ru": "Описание",
                "description_en": "Description",
            }
        ],
    }
