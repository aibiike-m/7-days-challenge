from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Challenge, Task
from .serializers import (
    ChallengeListSerializer,
    ChallengeDetailSerializer,
    ChallengeCreateSerializer,
    TaskSerializer,
)
from .services.challenge_service import ChallengeService


class ChallengeViewSet(viewsets.ModelViewSet):
    """API для работы с челленджами"""

    permission_classes = [IsAuthenticated]  

    def get_queryset(self):
        return Challenge.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    queryset = Challenge.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return ChallengeListSerializer
        elif self.action == "create":
            return ChallengeCreateSerializer
        return ChallengeDetailSerializer

    def create(self, request):
        """Создание нового челленджа с генерацией задач через AI"""
        serializer = ChallengeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        goal = serializer.validated_data["goal"]

        try:
            challenge = ChallengeService.create_challenge_with_tasks(
                goal=goal, user=request.user  # ← ДОБАВЬТЕ
            )

            response_serializer = ChallengeDetailSerializer(challenge)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=["get"])
    def active(self, request):
        challenge = ChallengeService.get_active_challenge(request.user)  # ← ИСПРАВЬТЕ

        if not challenge:
            return Response(
                {"detail": "Нет активных челленджей"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ChallengeDetailSerializer(challenge)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(challenge__user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        challenge_ids = request.query_params.get("challenge_ids")
        if challenge_ids:
            ids_list = challenge_ids.split(",")
            queryset = queryset.filter(challenge__id__in=ids_list)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    queryset = Task.objects.all()
    serializer_class = TaskSerializer   
    pagination_class = None

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Отметить задачу как выполненную"""
        task = self.get_object()
        task.mark_completed()
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def uncomplete(self, request, pk=None):
        """Снять отметку о выполнении"""
        task = self.get_object()
        task.mark_uncompleted()
        serializer = self.get_serializer(task)
        return Response(serializer.data)
