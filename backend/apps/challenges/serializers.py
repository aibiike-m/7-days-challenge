from rest_framework import serializers
from .models import Challenge, Task


class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор для задач"""

    class Meta:
        model = Task
        fields = [
            "id",
            "day_number",
            "title",
            "description",
            "order",
            "is_completed",
            "completed_at",
        ]
        read_only_fields = ["id", "completed_at"]


class ChallengeListSerializer(serializers.ModelSerializer):
    """Для списка челленджей"""

    progress_percentage = serializers.ReadOnlyField()
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = [
            "id",
            "goal",
            "status",
            "created_at",
            "duration_days",
            "progress_percentage",
            "tasks_count",
        ]

    def get_tasks_count(self, obj):
        return obj.tasks.count()


class ChallengeDetailSerializer(serializers.ModelSerializer):
    """Информация о челлендже с задачами"""

    tasks = TaskSerializer(many=True, read_only=True)
    progress_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Challenge
        fields = [
            "id",
            "goal",
            "status",
            "created_at",
            "start_date",
            "duration_days",
            "progress_percentage",
            "tasks",
        ]


class ChallengeCreateSerializer(serializers.Serializer):
    """Создание челленджа"""

    goal = serializers.CharField(
        required=True,
        min_length=10,
        max_length=500,
        help_text="Цель, которую хотите достичь за 7 дней",
    )
