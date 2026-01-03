from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

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
                        "username": user.username,
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


@api_view(["POST"])
@permission_classes([AllowAny])
def google_login(request):

    token = request.data.get("token")
    idinfo = id_token.verify_oauth2_token(
        token, google_requests.Request(), settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
    )

    if not token:
        return Response(
            {"error": "Token not provided"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
        )

        email = idinfo["email"]
        name = idinfo.get("name", email)

        user, created = User.objects.get_or_create(
            email=email, defaults={"username": email.split("@")[0], "first_name": name}
        )

        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": user_data,
            }
        )
    except Exception as e:
        return Response(
            {"error": f"Invalid token or Google error: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
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
