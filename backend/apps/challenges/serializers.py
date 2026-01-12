from rest_framework import serializers
from django.utils import translation
from .models import Challenge, Task

class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = [
            "id",
            "challenge_id",
            "day_number",
            "title",  
            "description",
            "order",
            "is_completed",
            "completed_at",
        ]
        read_only_fields = ["id", "completed_at"]

    def to_representation(self, instance):
        lang = self.context.get("language", "ru")
        with translation.override(lang):
            return super().to_representation(instance)


class ChallengeListSerializer(serializers.ModelSerializer):

    progress_percentage = serializers.ReadOnlyField()
    tasks_count = serializers.SerializerMethodField()

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
            "tasks_count",
            "color",
        ]

    def get_tasks_count(self, obj):
        return obj.tasks.count()

    def to_representation(self, instance):
        lang = self.context.get("language", "ru")
        with translation.override(lang):
            return super().to_representation(instance)


class ChallengeDetailSerializer(serializers.ModelSerializer):

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
            "current_day",
            "color",
        ]

    def to_representation(self, instance):
        lang = self.context.get("language", "ru")
        with translation.override(lang):
            self.fields["tasks"].context["language"] = lang
            return super().to_representation(instance)


class ChallengeCreateSerializer(serializers.Serializer):

    goal = serializers.CharField(
        required=True,
        min_length=10,
        max_length=500,
    )
