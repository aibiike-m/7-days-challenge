from collections import defaultdict
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import (
    action,
    api_view,
    permission_classes,
    throttle_classes,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.challenges.models import Task
from apps.users.models import EmailVerification
from .serializers import (
    UserSerializer,
    ChangePasswordSerializer,
    SetPasswordSerializer,
    RequestEmailChangeSerializer,
    ConfirmEmailChangeSerializer,
)
from .throttles import EmailChangeRateThrottle, LoginRateThrottle


User = get_user_model()

@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
def login_by_email(request):
    email = request.data.get("email")
    password = request.data.get("password")
    if not email or not password:
        return Response(
            {"error": "Email and password required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user = authenticate(request, username=email, password=password)
    if user is not None:
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
        user = request.user
        today = timezone.localdate()

        start_of_week = today - timedelta(days=today.weekday())
        lang = request.query_params.get("language", user.language)
        weekdays = (
            ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
            if lang == "ru"
            else ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        )
        tasks = (
            Task.objects.filter(challenge__user=user, challenge__status="active")
            .select_related("challenge")
            .only("id", "day_number", "is_completed", "challenge__start_date")
        )
        days_data = defaultdict(lambda: {"total": 0, "completed": 0})
        for task in tasks:
            task_date = task.challenge.start_date + timedelta(days=task.day_number - 1)
            days_data[task_date]["total"] += 1
            if task.is_completed:
                days_data[task_date]["completed"] += 1
        stats = []
        for i in range(7):
            current_date = start_of_week + timedelta(days=i)
            day_data = days_data[current_date]
            total = day_data["total"]
            completed = day_data["completed"]
            percent = round((completed / total * 100)) if total > 0 else 0
            stats.append({"day": weekdays[i], "percent": percent})
        return Response(stats)
    @action(detail=False, methods=["post"], url_path="change-password")
    def change_password(self, request):
        user = request.user
        if not user.has_usable_password():
            return Response(
                {
                    "error": "You do not have a password set. Use the set password function."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Password changed successfully"}, status=status.HTTP_200_OK
        )
    @action(detail=False, methods=["post"], url_path="set-password")
    def set_password(self, request):
        user = request.user
        if user.has_usable_password():
            return Response(
                {
                    "error": "You already have a password set. Use the password change function."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = SetPasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "message": "Password set successfully. You can now log in with email and password."
            },
            status=status.HTTP_200_OK,
        )
    @action(
        detail=False,
        methods=["post"],
        url_path="request-email-change",
        throttle_classes=[EmailChangeRateThrottle],
    )
    def request_email_change(self, request):
        serializer = RequestEmailChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        new_email = serializer.validated_data["new_email"]
        user = request.user
        EmailVerification.objects.filter(
            user=user, is_used=False, is_cancelled=False
        ).update(is_cancelled=True)
        verification = EmailVerification.objects.create(user=user, new_email=new_email)
        confirm_url = f"{settings.FRONTEND_URL}/confirm-email-change?token={verification.confirm_token}"
        cancel_url = f"{settings.FRONTEND_URL}/cancel-email-change?token={verification.cancel_token}"
        send_mail(
            subject="Confirm your new email address",
            message=(
                f"You requested to change your email address.\n\n"
                f"To confirm, enter this code: {verification.code}\n\n"
                f"Or click the link: {confirm_url}\n\n"
                f"This code expires in 15 minutes."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[new_email],
        )
        send_mail(
            subject="Email change request",
            message=(
                f"Someone requested to change the email for your account to {new_email}.\n\n"
                f"If this was you, no action is needed — just confirm via the new email.\n\n"
                f"If this wasn't you, cancel the request immediately:\n{cancel_url}\n\n"
                f"The link expires in 15 minutes."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        return Response(
            {"message": "Verification code sent to your new email"},
            status=status.HTTP_200_OK,
        )
    @action(
        detail=False,
        methods=["post"],
        url_path="confirm-email-change",
        throttle_classes=[EmailChangeRateThrottle],
    )
    def confirm_email_change(self, request):
        serializer = ConfirmEmailChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"]
        user = request.user
        verification = (
            EmailVerification.objects.filter(
                user=user, code=code, is_used=False, is_cancelled=False
            )
            .order_by("-created_at")
            .first()
        )
        if not verification or not verification.is_valid():
            return Response(
                {"error": "Invalid or expired verification code"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        old_email = user.email
        user.email = verification.new_email
        user.save(update_fields=["email"])
        verification.is_used = True
        verification.save(update_fields=["is_used"])
        EmailVerification.objects.filter(
            user=user, is_used=False, is_cancelled=False
        ).exclude(pk=verification.pk).update(is_cancelled=True)
        send_mail(
            subject="Your email address has been changed",
            message=(
                f"Your email address has been successfully changed to {verification.new_email}.\n\n"
                f"If you didn't do this, please contact support immediately."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[old_email],
        )
        return Response(
            {
                "message": "Email changed successfully. Please log in again.",
                "new_email": verification.new_email,
            },
            status=status.HTTP_200_OK,
        )
    @action(detail=False, methods=["get"], url_path="has-password")
    def has_password(self, request):
        return Response({"has_password": request.user.has_usable_password()})

@api_view(["GET"])
@permission_classes([AllowAny])
def cancel_email_change(request):
    token = request.query_params.get("token")
    if not token:
        return Response(
            {"error": "Token not provided"}, status=status.HTTP_400_BAD_REQUEST
        )
    verification = EmailVerification.objects.filter(
        cancel_token=token,
        is_used=False,
        is_cancelled=False,
    ).first()
    if not verification:
        return Response(
            {"error": "Invalid or already used cancellation link"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not verification.is_valid():
        return Response(
            {"error": "This cancellation link has expired"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    verification.is_cancelled = True
    verification.save(update_fields=["is_cancelled"])
    return Response(
        {"message": "Email change request has been cancelled successfully."},
        status=status.HTTP_200_OK,
    )

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        refresh = request.data.get("refresh")
        if refresh:
            try:
                token = RefreshToken(refresh)
                token.blacklist()
            except Exception:
                pass
        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )
