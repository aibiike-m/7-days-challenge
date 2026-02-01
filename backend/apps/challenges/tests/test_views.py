import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework import status

from apps.challenges.models import Challenge, Task
from apps.challenges.constants import STATUS_ACTIVE, STATUS_COMPLETED


@pytest.mark.django_db
class TestChallengeListAPI:

    def test_list_challenges_unauthenticated(self, api_client):
        response = api_client.get("/api/challenges/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_challenges_empty(self, authenticated_client):
        response = authenticated_client.get("/api/challenges/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_list_challenges_authenticated(self, authenticated_client, challenge):
        response = authenticated_client.get("/api/challenges/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["goal"] == challenge.goal
        assert response.data[0]["status"] == challenge.status
        assert "progress_percentage" in response.data[0]
        assert "tasks_count" in response.data[0]

    def test_list_challenges_filters_by_user(
        self, authenticated_client, user, other_user
    ):
        my_challenge = Challenge.objects.create(user=user, goal="My challenge")

        Challenge.objects.create(user=other_user, goal="Other's challenge")

        response = authenticated_client.get("/api/challenges/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["goal"] == "My challenge"

    def test_list_challenges_ordered_by_created_at(self, authenticated_client, user):
        old_challenge = Challenge.objects.create(user=user, goal="Old")
        old_challenge.created_at = timezone.now() - timedelta(days=5)
        old_challenge.save()

        new_challenge = Challenge.objects.create(user=user, goal="New")

        response = authenticated_client.get("/api/challenges/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        assert response.data[0]["goal"] == "New"
        assert response.data[1]["goal"] == "Old"


@pytest.mark.django_db
class TestChallengeDetailAPI:

    def test_retrieve_challenge(self, authenticated_client, challenge):
        response = authenticated_client.get(f"/api/challenges/{challenge.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["goal"] == challenge.goal
        assert response.data["status"] == challenge.status
        assert "tasks" in response.data
        assert "progress_percentage" in response.data
        assert "current_day" in response.data

    def test_retrieve_challenge_unauthenticated(self, api_client, challenge):
        response = api_client.get(f"/api/challenges/{challenge.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_other_user_challenge(self, authenticated_client, other_user):
        other_challenge = Challenge.objects.create(
            user=other_user, goal="Other's challenge"
        )

        response = authenticated_client.get(f"/api/challenges/{other_challenge.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_nonexistent_challenge(self, authenticated_client):
        response = authenticated_client.get("/api/challenges/99999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestChallengeActiveAPI:

    def test_get_active_challenge(self, authenticated_client, user):
        old_challenge = Challenge.objects.create(
            user=user,
            goal="Old challenge",
            status=STATUS_ACTIVE,
        )
        old_challenge.created_at = timezone.now() - timedelta(days=5)
        old_challenge.save()

        new_challenge = Challenge.objects.create(
            user=user,
            goal="New challenge",
            status=STATUS_ACTIVE,
        )

        response = authenticated_client.get("/api/challenges/active/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["goal"] == "New challenge"
        assert response.data["id"] == new_challenge.id

    def test_get_active_challenge_not_found(self, authenticated_client, user):
        Challenge.objects.create(
            user=user,
            goal="Completed",
            status=STATUS_COMPLETED,
        )

        response = authenticated_client.get("/api/challenges/active/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_active_challenge_empty(self, authenticated_client):
        response = authenticated_client.get("/api/challenges/active/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestTaskListAPI:

    def test_list_tasks_unauthenticated(self, api_client):
        response = api_client.get("/api/tasks/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_tasks_authenticated(self, authenticated_client, task):
        response = authenticated_client.get("/api/tasks/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["title"] == task.title
        assert response.data[0]["day_number"] == task.day_number

    def test_list_tasks_filtered_by_challenge(self, authenticated_client, user):
        challenge1 = Challenge.objects.create(user=user, goal="Challenge 1")
        challenge2 = Challenge.objects.create(user=user, goal="Challenge 2")

        task1 = Task.objects.create(
            challenge=challenge1,
            day_number=1,
            title="Task 1",
            description="Desc",
            order=1,
        )
        task2 = Task.objects.create(
            challenge=challenge2,
            day_number=1,
            title="Task 2",
            description="Desc",
            order=1,
        )

        response = authenticated_client.get(
            f"/api/tasks/?challenge_ids={challenge1.id}"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Task 1"

    def test_list_tasks_filtered_by_multiple_challenges(
        self, authenticated_client, user
    ):
        challenge1 = Challenge.objects.create(user=user, goal="Challenge 1")
        challenge2 = Challenge.objects.create(user=user, goal="Challenge 2")
        challenge3 = Challenge.objects.create(user=user, goal="Challenge 3")

        task1 = Task.objects.create(
            challenge=challenge1, day_number=1, title="T1", description="D", order=1
        )
        task2 = Task.objects.create(
            challenge=challenge2, day_number=1, title="T2", description="D", order=1
        )
        task3 = Task.objects.create(
            challenge=challenge3, day_number=1, title="T3", description="D", order=1
        )

        response = authenticated_client.get(
            f"/api/tasks/?challenge_ids={challenge1.id},{challenge2.id}"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_list_tasks_invalid_challenge_ids(self, authenticated_client):
        response = authenticated_client.get("/api/tasks/?challenge_ids=abc,def")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid challenge_ids format" in response.data["error"]

    def test_list_tasks_filters_by_user(self, authenticated_client, user, other_user):
        my_challenge = Challenge.objects.create(user=user, goal="My")
        other_challenge = Challenge.objects.create(user=other_user, goal="Other")

        my_task = Task.objects.create(
            challenge=my_challenge,
            day_number=1,
            title="My task",
            description="D",
            order=1,
        )
        other_task = Task.objects.create(
            challenge=other_challenge,
            day_number=1,
            title="Other task",
            description="D",
            order=1,
        )

        response = authenticated_client.get("/api/tasks/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["title"] == "My task"


@pytest.mark.django_db
class TestTaskCompleteAPI:

    def test_complete_task(self, authenticated_client, task):
        assert task.is_completed is False

        response = authenticated_client.post(f"/api/tasks/{task.id}/complete/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_completed"] is True
        assert response.data["completed_at"] is not None

        task.refresh_from_db()
        assert task.is_completed is True

    def test_complete_task_unauthenticated(self, api_client, task):
        response = api_client.post(f"/api/tasks/{task.id}/complete/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_complete_future_task(self, authenticated_client, challenge):
        future_task = Task.objects.create(
            challenge=challenge,
            day_number=10,
            title="Future task",
            description="Test",
            order=1,
        )

        response = authenticated_client.post(f"/api/tasks/{future_task.id}/complete/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "cannot_modify_future_tasks" in response.data["detail"]

        future_task.refresh_from_db()
        assert future_task.is_completed is False

    def test_complete_task_idempotent(self, authenticated_client, completed_task):
        first_completed_at = completed_task.completed_at

        response = authenticated_client.post(
            f"/api/tasks/{completed_task.id}/complete/"
        )

        assert response.status_code == status.HTTP_200_OK

        completed_task.refresh_from_db()
        assert completed_task.completed_at == first_completed_at


@pytest.mark.django_db
class TestTaskUncompleteAPI:

    def test_uncomplete_task(self, authenticated_client, completed_task):
        assert completed_task.is_completed is True

        response = authenticated_client.post(
            f"/api/tasks/{completed_task.id}/uncomplete/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_completed"] is False
        assert response.data["completed_at"] is None

        completed_task.refresh_from_db()
        assert completed_task.is_completed is False

    def test_uncomplete_task_unauthenticated(self, api_client, completed_task):
        response = api_client.post(f"/api/tasks/{completed_task.id}/uncomplete/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_uncomplete_future_task(self, authenticated_client, challenge):
        future_task = Task.objects.create(
            challenge=challenge,
            day_number=10,
            title="Future task",
            description="Test",
            order=1,
        )
        future_task.mark_completed()

        response = authenticated_client.post(f"/api/tasks/{future_task.id}/uncomplete/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_uncomplete_task_idempotent(self, authenticated_client, task):
        assert task.is_completed is False

        response = authenticated_client.post(f"/api/tasks/{task.id}/uncomplete/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_completed"] is False
