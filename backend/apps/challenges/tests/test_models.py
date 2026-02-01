import pytest
from datetime import date

from apps.challenges.models import Challenge, Task
from apps.challenges.constants import (
    CHALLENGE_DURATION_DAYS,
    CHALLENGE_COLORS,
    STATUS_ACTIVE,
)


@pytest.mark.django_db
class TestChallengeModel:
    def test_challenge_creation(self, user):
        challenge = Challenge.objects.create(
            user=user,
            goal="Test goal",
            status=STATUS_ACTIVE,
        )
        assert challenge.user == user
        assert challenge.goal == "Test goal"
        assert challenge.status == STATUS_ACTIVE
        assert challenge.duration_days == CHALLENGE_DURATION_DAYS
        assert challenge.current_day == 1
        assert challenge.start_date == date.today()

    def test_challenge_str_representation(self, challenge):
        assert str(challenge) == f"Challenge: {challenge.goal[:50]}"

    def test_challenge_str_truncates_long_goals(self, user):
        long_goal = "A" * 100
        challenge = Challenge.objects.create(
            user=user,
            goal=long_goal,
        )
        assert str(challenge) == f"Challenge: {long_goal[:50]}"
        assert len(str(challenge)) == len("Challenge: ") + 50

    def test_challenge_color_auto_assignment(self, user):
        challenge = Challenge.objects.create(
            user=user,
            goal="Test goal",
        )
        assert challenge.color in CHALLENGE_COLORS
        assert challenge.color != ""

    def test_challenge_color_rotation(self, user):
        challenges = []
        num_challenges = len(CHALLENGE_COLORS) + 3
        for i in range(num_challenges):
            challenge = Challenge.objects.create(
                user=user,
                goal=f"Goal {i}",
            )
            challenges.append(challenge)
        assert challenges[0].color == CHALLENGE_COLORS[0]
        assert challenges[1].color == CHALLENGE_COLORS[1]
        assert challenges[len(CHALLENGE_COLORS)].color == CHALLENGE_COLORS[0]
        assert challenges[len(CHALLENGE_COLORS) + 1].color == CHALLENGE_COLORS[1]

    def test_challenge_custom_color_preserved(self, user):
        custom_color = "#FF0000"
        challenge = Challenge.objects.create(user=user, goal="Test", color=custom_color)
        assert challenge.color == custom_color

    def test_progress_percentage_no_tasks(self, challenge):
        assert challenge.progress_percentage == 0

    def test_progress_percentage_with_tasks(self, challenge):
        tasks = []
        for i in range(5):
            task = Task.objects.create(
                challenge=challenge,
                day_number=1,
                title=f"Task {i}",
                description="Test",
                order=i,
            )
            tasks.append(task)
        assert challenge.progress_percentage == 0
        tasks[0].mark_completed()
        tasks[1].mark_completed()
        assert challenge.progress_percentage == 40
        tasks[2].mark_completed()
        tasks[3].mark_completed()
        tasks[4].mark_completed()
        assert challenge.progress_percentage == 100

    def test_challenge_ordering(self, user):
        from datetime import timedelta
        from django.utils import timezone
        now = timezone.now()
        challenge1 = Challenge.objects.create(user=user, goal="First")
        challenge1.created_at = now - timedelta(seconds=3)
        challenge1.save()
        challenge2 = Challenge.objects.create(user=user, goal="Second")
        challenge2.created_at = now - timedelta(seconds=2)
        challenge2.save()
        challenge3 = Challenge.objects.create(user=user, goal="Third")
        challenge3.created_at = now - timedelta(seconds=1)
        challenge3.save()
        challenges = Challenge.objects.filter(user=user)
        assert challenges[0] == challenge3
        assert challenges[1] == challenge2
        assert challenges[2] == challenge1


@pytest.mark.django_db
class TestTaskModel:
    def test_task_creation(self, challenge):
        task = Task.objects.create(
            challenge=challenge,
            day_number=1,
            title="Test task",
            description="Test description",
            order=1,
        )
        assert task.challenge == challenge
        assert task.day_number == 1
        assert task.title == "Test task"
        assert task.description == "Test description"
        assert task.order == 1
        assert task.is_completed is False
        assert task.completed_at is None

    def test_task_str_representation(self, task):
        expected = f"Day {task.day_number}: {task.title}"
        assert str(task) == expected

    def test_mark_completed(self, task):
        assert task.is_completed is False
        assert task.completed_at is None
        task.mark_completed()
        assert task.is_completed is True
        assert task.completed_at is not None

    def test_mark_completed_idempotent(self, task):
        task.mark_completed()
        first_completed_at = task.completed_at
        task.mark_completed()
        assert task.completed_at == first_completed_at

    def test_mark_uncompleted(self, task):
        task.mark_completed()
        assert task.is_completed is True
        task.mark_uncompleted()
        assert task.is_completed is False
        assert task.completed_at is None

    def test_mark_uncompleted_idempotent(self, task):
        task.mark_uncompleted()
        task.mark_uncompleted()
        assert task.is_completed is False
        assert task.completed_at is None

    def test_current_day_advances_when_all_tasks_completed(self, challenge):
        tasks = []
        for i in range(3):
            task = Task.objects.create(
                challenge=challenge,
                day_number=1,
                title=f"Task {i}",
                description="Test",
                order=i,
            )
            tasks.append(task)
        assert challenge.current_day == 1
        tasks[0].mark_completed()
        tasks[1].mark_completed()
        challenge.refresh_from_db()
        assert challenge.current_day == 1
        tasks[2].mark_completed()
        challenge.refresh_from_db()
        assert challenge.current_day == 2

    def test_current_day_doesnt_advance_for_other_days(self, challenge):
        task_day1 = Task.objects.create(
            challenge=challenge,
            day_number=1,
            title="Day 1 task",
            description="Test",
            order=1,
        )
        task_day3 = Task.objects.create(
            challenge=challenge,
            day_number=3,
            title="Day 3 task",
            description="Test",
            order=1,
        )
        assert challenge.current_day == 1
        task_day3.mark_completed()
        challenge.refresh_from_db()
        assert challenge.current_day == 1

    def test_current_day_rewinds_on_uncomplete(self, challenge):
        tasks_day1 = []
        for i in range(2):
            task = Task.objects.create(
                challenge=challenge,
                day_number=1,
                title=f"Day 1 Task {i}",
                description="Test",
                order=i,
            )
            task.mark_completed()
            tasks_day1.append(task)
        challenge.refresh_from_db()
        assert challenge.current_day == 2
        Task.objects.create(
            challenge=challenge,
            day_number=2,
            title="Day 2 task",
            description="Test",
            order=1,
        )
        tasks_day1[0].mark_uncompleted()
        challenge.refresh_from_db()
        assert challenge.current_day == 1

    def test_task_ordering(self, challenge):
        task1 = Task.objects.create(
            challenge=challenge,
            day_number=2,
            title="Day 2 Task 1",
            description="Test",
            order=1,
        )
        task2 = Task.objects.create(
            challenge=challenge,
            day_number=1,
            title="Day 1 Task 1",
            description="Test",
            order=1,
        )
        task3 = Task.objects.create(
            challenge=challenge,
            day_number=1,
            title="Day 1 Task 2",
            description="Test",
            order=2,
        )
        tasks = challenge.tasks.all()
        assert tasks[0] == task2
        assert tasks[1] == task3
        assert tasks[2] == task1

    def test_uncomplete_does_not_rewind_on_empty_current_day(self, challenge):
        challenge.current_day = 3
        challenge.save()
        task_day1 = Task.objects.create(
            challenge=challenge, day_number=1, title="Task", description="Desc", order=1
        )
        task_day1.mark_completed()
        task_day1.mark_uncompleted()
        challenge.refresh_from_db()
        assert challenge.current_day == 3
