from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from datetime import datetime, timedelta

from apps.challenges.models import Task
from .serializers import UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.none()

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="stats/weekly")
    def weekly_stats(self, request):
        user = request.user
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())

        stats = []
        weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

        for i in range(7):
            current_date = start_of_week + timedelta(days=i)

            all_tasks = Task.objects.filter(
                challenge__user=user, challenge__status="active"
            )

            total = 0
            completed = 0

            for task in all_tasks:
                try:
                    task_date = task.challenge.start_date + timedelta(
                        days=task.day_number - 1
                    )
                    if task_date == current_date:
                        total += 1
                        if task.is_completed:
                            completed += 1
                except Exception:
                    continue

            percent = round((completed / total * 100)) if total > 0 else 0
            stats.append(
                {
                    "day": weekdays[i],
                    "percent": percent,
                }
            )

        return Response(stats)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Пользователь существует"}, status=status.HTTP_400_BAD_REQUEST
            )

        User.objects.create_user(username=username, email=email, password=password)
        return Response({"success": True}, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    def post(self, request):
        response = Response({"message": "Logged out"})
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response
