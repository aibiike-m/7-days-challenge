from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta

from apps.challenges.models import Task
from .serializers import UserSerializer

User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def login_by_email(request):
    """Login by email"""
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"error": "Email and password required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)
        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": {
                        "id": user.id,
                        "email": user.email,  
                        "language": user.language,
                    },
                }
            )
    except User.DoesNotExist:
        pass

    return Response(
        {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
    )


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        user = request.user
        if request.method == "PATCH":
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="stats/weekly")
    def weekly_stats(self, request):
        """Get statistics for the week"""
        user = request.user
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())

        lang = request.query_params.get("language", user.language)
        weekdays = (
            ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
            if lang == "ru"
            else ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        )

        all_tasks = Task.objects.filter(
            challenge__user=user, challenge__status="active"
        ).select_related("challenge")

        stats = []
        for i in range(7):
            current_date = start_of_week + timedelta(days=i)

            day_tasks = [
                t
                for t in all_tasks
                if (t.challenge.start_date + timedelta(days=t.day_number - 1))
                == current_date
            ]

            total = len(day_tasks)
            completed = len([t for t in day_tasks if t.is_completed])

            percent = round((completed / total * 100)) if total > 0 else 0
            stats.append(
                {
                    "day": weekdays[i],
                    "percent": percent,
                }
            )

        return Response(stats)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass

        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )