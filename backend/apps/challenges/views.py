from rest_framework import viewsets, status
from rest_framework.decorators import action, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils.translation import gettext as _
import logging

from .models import Challenge, Task
from .serializers import (
    ChallengeListSerializer,
    ChallengeCreateSerializer,
    ChallengeDetailSerializer,
    TaskSerializer,
)
from .services.challenge_service import ChallengeService

from apps.users.throttles import ChallengeCreationThrottle
from rest_framework.throttling import UserRateThrottle

logger = logging.getLogger(__name__)


class ChallengeViewSet(viewsets.ModelViewSet):
    """
    API for working with challenges.
    
    Security features:
    - Throttling on challenge creation (10/hour)
    - Active challenges limit (10 max)
    - Daily creation limit (15 max)
    """

    permission_classes = [IsAuthenticated]
    queryset = Challenge.objects.none()

    def get_queryset(self):
        return Challenge.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ChallengeListSerializer
        elif self.action == "create":
            return ChallengeCreateSerializer
        return ChallengeDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        lang = self.request.query_params.get("language") or self.request.user.language
        context["language"] = lang
        return context

    def get_throttles(self):
        if self.action == 'create':
            return [ChallengeCreationThrottle()]
        return super().get_throttles()

    def create(self, request):
        serializer = ChallengeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        goal = serializer.validated_data["goal"]
        lang = request.query_params.get("language") or request.user.language

        try:
            challenge = ChallengeService.create_challenge_with_tasks(
                goal=goal, user=request.user, language=lang
            )

            response_serializer = ChallengeDetailSerializer(
                challenge, context=self.get_serializer_context()
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            logger.warning(
                f"Challenge creation failed: user={request.user.email}, "
                f"error={str(e)}"
            )
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(
                f"Unexpected error creating challenge: user={request.user.email}, "
                f"error={str(e)}"
            )
            return Response(
                {"error": "Failed to create challenge. Please try again later."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(
            queryset, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def active(self, request):
        challenge = ChallengeService.get_active_challenge(request.user)

        if not challenge:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ChallengeDetailSerializer(
            challenge, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="creation-stats")
    def creation_stats(self, request):
        stats = ChallengeService.get_user_stats(request.user)
        return Response(stats)

    @action(detail=False, methods=["delete"], url_path="bulk-delete")
    @throttle_classes([UserRateThrottle])

    def bulk_delete(self, request):
        ids = request.data.get("ids", [])
        if not ids:
            return Response(
                {"detail": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        if len(ids) > 10:
            return Response({"detail": "Too many IDs"}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count, _ = self.get_queryset().filter(id__in=ids).delete()

        logger.info(
            f"Bulk delete: user={request.user.email}, deleted={deleted_count}"
        )

        return Response(
            {"detail": f"Successfully deleted {deleted_count} challenges"},
            status=status.HTTP_204_NO_CONTENT,
        )


class TaskViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated]
    queryset = Task.objects.none()
    serializer_class = TaskSerializer
    pagination_class = None

    def get_queryset(self):
        return Task.objects.filter(challenge__user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        lang = self.request.query_params.get("language") or self.request.user.language
        context["language"] = lang
        return context

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        challenge_ids = request.query_params.get("challenge_ids")

        if challenge_ids:
            try:
                ids_list = [
                    int(id.strip()) for id in challenge_ids.split(",") if id.strip()
                ]
                queryset = queryset.filter(challenge__id__in=ids_list)
            except ValueError:
                return Response(
                    {"error": "Invalid challenge_ids format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = self.get_serializer(
            queryset, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    def _validate_task_modification(self, task):
        """
        Checks whether editing (checking/unchecking) a task is allowed.

        Allowed: tasks for today and in the past.
        Prohibited: tasks for future days.

        Returns:
            tuple[bool, str | None]: (allowed, error message, or None)
        """
        challenge = task.challenge
        task_date = challenge.start_date + timedelta(days=task.day_number - 1)
        today = timezone.now().date()

        if task_date > today:
            return False, _("cannot_modify_future_tasks")

        return True, None

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()

        allowed, error_msg = self._validate_task_modification(task)
        if not allowed:
            return Response(
                {"detail": error_msg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task.mark_completed()
        serializer = self.get_serializer(task, context=self.get_serializer_context())
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def uncomplete(self, request, pk=None):
        task = self.get_object()

        allowed, error_msg = self._validate_task_modification(task)
        if not allowed:
            return Response(
                {"detail": error_msg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task.mark_uncompleted()
        serializer = self.get_serializer(task, context=self.get_serializer_context())
        return Response(serializer.data)
