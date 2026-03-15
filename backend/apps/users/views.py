from collections import defaultdict
from datetime import timedelta
import logging

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
from axes.models import AccessAttempt
from axes.handlers.proxy import AxesProxyHandler

from apps.challenges.models import Task
from apps.challenges.constants import APP_NAME
from apps.users.models import EmailVerification, AccountDeletion, PasswordResetCode
from .serializers import (
    UserSerializer,
    ChangePasswordSerializer,
    SetPasswordSerializer,
    RequestEmailChangeSerializer,
    ConfirmEmailChangeSerializer,
    DeleteAccountWithPasswordSerializer,
    RequestPasswordResetSerializer,
    ConfirmPasswordResetSerializer,
)
from .throttles import (
    EmailChangeRateThrottle,
    LoginRateThrottle,
    PasswordResetRateThrottle,
    CodeSendingThrottle,
    TokenActionThrottle,
    VerificationCodeRateThrottle,
    PasswordChangeRateThrottle,
)


User = get_user_model()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Email helpers
# ---------------------------------------------------------------------------


def _t(lang, ru_text, en_text):
    """Return text in the given language (ru or en)."""
    return ru_text if lang == "ru" else en_text


def send_localized_mail(
    subject_ru, subject_en, message_ru, message_en, recipient, lang
):
    subject = _t(lang, subject_ru, subject_en)
    message = _t(lang, message_ru, message_en)
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
    )


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------


def get_remaining_minutes(email):
    from axes.conf import settings as axes_settings

    attempt = (
        AccessAttempt.objects.filter(username=email).order_by("-attempt_time").first()
    )

    if attempt:
        cooloff = getattr(axes_settings, "AXES_COOLOFF_TIME", timedelta(minutes=15))
        if isinstance(cooloff, int):
            cooloff = timedelta(seconds=cooloff)

        unlock_time = attempt.attempt_time + cooloff
        remaining = unlock_time - timezone.now()
        return max(int(remaining.total_seconds() / 60), 1)

    return 15


# ---------------------------------------------------------------------------
# Auth views
# ---------------------------------------------------------------------------


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
def login_by_email(request):
    email = request.data.get("email")
    password = request.data.get("password")

    handler = AxesProxyHandler()

    if handler.is_locked(request, credentials={"username": email}):
        minutes = get_remaining_minutes(email)
        logger.warning(
            f"Blocked login attempt for {email} from {request.META.get('REMOTE_ADDR')}"
        )
        return Response(
            {"error": "locked", "minutes": minutes},
            status=status.HTTP_403_FORBIDDEN,
        )

    user = authenticate(request, username=email, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data,
            }
        )
    else:
        return Response(
            {"error": "invalid_credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


# ---------------------------------------------------------------------------
# User viewset
# ---------------------------------------------------------------------------


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    http_method_names = ["get", "post", "patch", "head", "options"]

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

    @action(
        detail=False,
        methods=["post"],
        url_path="change-password",
        throttle_classes=[PasswordChangeRateThrottle],
    )
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

    @action(
        detail=False,
        methods=["post"],
        url_path="set-password",
        throttle_classes=[PasswordChangeRateThrottle],
    )
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

    @action(detail=False, methods=["get"], url_path="has-password")
    def has_password(self, request):
        return Response({"has_password": request.user.has_usable_password()})

    @action(
        detail=False,
        methods=["post"],
        url_path="request-email-change",
        throttle_classes=[CodeSendingThrottle, EmailChangeRateThrottle],
    )
    def request_email_change(self, request):
        serializer = RequestEmailChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        new_email = serializer.validated_data["new_email"]
        user = request.user
        lang = user.language

        EmailVerification.objects.filter(
            user=user, is_used=False, is_cancelled=False
        ).update(is_cancelled=True)

        verification = EmailVerification.objects.create(
            user=user,
            old_email=user.email,
            new_email=new_email,
        )

        cancel_url = f"{settings.FRONTEND_URL}/cancel-email-change?token={verification.cancel_token}"

        send_localized_mail(
            subject_ru=f"{APP_NAME} — Подтвердите новый email",
            subject_en=f"{APP_NAME} — Confirm your new email address",
            message_ru=(
                f"Вы запросили смену email-адреса.\n\n"
                f"Для подтверждения введите этот код: {verification.code}\n\n"
                f"Код действителен 15 минут.\n\n"
                f"Если вы не запрашивали смену email — просто проигнорируйте это письмо.\n\n"
                f"— {APP_NAME}"
            ),
            message_en=(
                f"You requested to change your email address.\n\n"
                f"To confirm, enter this code: {verification.code}\n\n"
                f"This code expires in 15 minutes.\n\n"
                f"If you didn't request this, you can safely ignore this email.\n\n"
                f"— {APP_NAME}"
            ),
            recipient=new_email,
            lang=lang,
        )

        send_localized_mail(
            subject_ru=f"{APP_NAME} — Запрос на смену email",
            subject_en=f"{APP_NAME} — Email change request",
            message_ru=(
                f"Кто-то запросил смену email вашего аккаунта на {new_email}.\n\n"
                f"Если это были вы — ничего делать не нужно, просто подтвердите через новый email.\n\n"
                f"Если это были не вы — немедленно отмените запрос по ссылке:\n{cancel_url}\n\n"
                f"Ссылка действительна 15 минут.\n\n"
                f"— {APP_NAME}"
            ),
            message_en=(
                f"Someone requested to change the email for your account to {new_email}.\n\n"
                f"If this was you, no action is needed — just confirm via the new email.\n\n"
                f"If this wasn't you, cancel the request immediately:\n{cancel_url}\n\n"
                f"The link expires in 15 minutes.\n\n"
                f"— {APP_NAME}"
            ),
            recipient=user.email,
            lang=lang,
        )

        return Response(
            {"message": f"Verification code sent to {new_email}"},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="confirm-email-change",
        throttle_classes=[VerificationCodeRateThrottle],
    )
    def confirm_email_change(self, request):
        serializer = ConfirmEmailChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"]
        user = request.user
        lang = user.language

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

        send_localized_mail(
            subject_ru=f"{APP_NAME} — Email успешно изменён",
            subject_en=f"{APP_NAME} — Your email has been changed",
            message_ru=(
                f"Ваш email-адрес успешно изменён с {old_email} на {user.email}.\n\n"
                f"— {APP_NAME}"
            ),
            message_en=(
                f"Your email address has been successfully changed from {old_email} to {user.email}.\n\n"
                f"— {APP_NAME}"
            ),
            recipient=old_email,
            lang=lang,
        )

        return Response(
            {"message": "Email changed successfully", "new_email": user.email},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="delete-account",
        throttle_classes=[CodeSendingThrottle],
    )
    def delete_account(self, request):
        serializer = DeleteAccountWithPasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        lang = user.language

        if user.has_usable_password():
            email = user.email
            user.delete()

            send_localized_mail(
                subject_ru=f"{APP_NAME} — Аккаунт удалён",
                subject_en=f"{APP_NAME} — Your account has been deleted",
                message_ru=(
                    f"Ваш аккаунт был безвозвратно удалён.\n\n"
                    f"— {APP_NAME}"
                ),
                message_en=(
                    f"Your account has been permanently deleted.\n\n"
                    f"— {APP_NAME}"
                ),
                recipient=email,
                lang=lang,
            )

            return Response(
                {"message": "Your account has been permanently deleted."},
                status=status.HTTP_200_OK,
            )

        else:
            AccountDeletion.objects.filter(user=user, is_used=False).update(is_used=True)
            deletion = AccountDeletion.objects.create(user=user)
            delete_url = (
                f"{settings.FRONTEND_URL}/confirm-account-deletion?token={deletion.token}"
            )

            send_localized_mail(
                subject_ru=f"{APP_NAME} — Подтвердите удаление аккаунта",
                subject_en=f"{APP_NAME} — Confirm account deletion",
                message_ru=(
                    f"Вы запросили удаление вашего аккаунта.\n\n"
                    f"Для подтверждения перейдите по ссылке:\n{delete_url}\n\n"
                    f"Ссылка действительна 1 час.\n\n"
                    f"Если вы не запрашивали это — просто проигнорируйте письмо, аккаунт останется активным.\n\n"
                    f"— {APP_NAME}"
                ),
                message_en=(
                    f"You requested to delete your account.\n\n"
                    f"To confirm, click this link:\n{delete_url}\n\n"
                    f"This link expires in 1 hour.\n\n"
                    f"If you didn't request this, you can safely ignore this email and your account will remain active.\n\n"
                    f"— {APP_NAME}"
                ),
                recipient=user.email,
                lang=lang,
            )

            return Response(
                {"message": "Confirmation email sent. Check your inbox."},
                status=status.HTTP_200_OK,
            )

# ---------------------------------------------------------------------------
# Email change cancellation
# ---------------------------------------------------------------------------


@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([TokenActionThrottle])
def cancel_email_change(request):
    token = request.query_params.get("token")
    if not token:
        return Response(
            {"error": "Token not provided"}, status=status.HTTP_400_BAD_REQUEST
        )
    verification = EmailVerification.objects.filter(
        cancel_token=token, is_cancelled=False
    ).first()
    if not verification:
        return Response(
            {"error": "Invalid or already used cancellation link"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not verification.is_valid() and not verification.is_used:
        return Response(
            {"error": "This cancellation link has expired"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    email_was_changed = verification.is_used
    lang = verification.user.language

    if email_was_changed:
        user = verification.user
        user.email = verification.old_email
        user.save(update_fields=["email"])

        send_localized_mail(
            subject_ru=f"{APP_NAME} — Email восстановлен",
            subject_en=f"{APP_NAME} — Your email has been restored",
            message_ru=(
                f"Ваш email-адрес восстановлен: {verification.old_email}.\n\n"
                f"Несанкционированная смена на {verification.new_email} была отменена.\n\n"
                f"— {APP_NAME}"
            ),
            message_en=(
                f"Your email address has been restored to {verification.old_email}.\n\n"
                f"The unauthorized change to {verification.new_email} has been cancelled.\n\n"
                f"— {APP_NAME}"
            ),
            recipient=verification.old_email,
            lang=lang,
        )

        send_localized_mail(
            subject_ru=f"{APP_NAME} — Смена email отменена",
            subject_en=f"{APP_NAME} — Email change cancelled",
            message_ru=(
                f"Смена email на {verification.new_email} была отменена владельцем аккаунта.\n\n"
                f"Аккаунт восстановлен на прежний адрес: {verification.old_email}.\n\n"
                f"— {APP_NAME}"
            ),
            message_en=(
                f"The email change to {verification.new_email} has been cancelled by the account owner.\n\n"
                f"The account email has been restored to {verification.old_email}.\n\n"
                f"— {APP_NAME}"
            ),
            recipient=verification.new_email,
            lang=lang,
        )

    verification.is_cancelled = True
    verification.save(update_fields=["is_cancelled"])

    message = (
        "Email change has been cancelled and your original email has been restored."
        if email_was_changed
        else "Email change request has been cancelled successfully."
    )

    return Response(
        {
            "message": message,
            "email_was_restored": email_was_changed,
        },
        status=status.HTTP_200_OK,
    )


# ---------------------------------------------------------------------------
# Account deletion confirmation
# ---------------------------------------------------------------------------


@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([TokenActionThrottle])
def confirm_delete_account(request):
    token = request.query_params.get("token")
    if not token:
        return Response(
            {"error": "Token not provided"}, status=status.HTTP_400_BAD_REQUEST
        )
    deletion = AccountDeletion.objects.filter(token=token, is_used=False).first()
    if not deletion:
        return Response(
            {"error": "Invalid or already used deletion link"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not deletion.is_valid():
        return Response(
            {"error": "This deletion link has expired"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = deletion.user
    email = user.email
    lang = user.language

    deletion.is_used = True
    deletion.save(update_fields=["is_used"])
    user.delete()

    send_localized_mail(
        subject_ru=f"{APP_NAME} — Аккаунт удалён",
        subject_en=f"{APP_NAME} — Your account has been deleted",
        message_ru=(
            f"Ваш аккаунт был безвозвратно удалён.\n\n"
            f"— {APP_NAME}"
        ),
        message_en=(
            f"Your account has been permanently deleted.\n\n"
            f"— {APP_NAME}"
        ),
        recipient=email,
        lang=lang,
    )

    return Response(
        {"message": "Your account has been permanently deleted."},
        status=status.HTTP_200_OK,
    )


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Password reset
# ---------------------------------------------------------------------------


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([CodeSendingThrottle, PasswordResetRateThrottle])
def request_password_reset(request):
    serializer = RequestPasswordResetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data["email"]

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {"message": "If this email is registered, you will receive a reset code."},
            status=status.HTTP_200_OK,
        )

    if not user.has_usable_password():
        return Response(
            {"message": "If this email is registered, you will receive a reset code."},
            status=status.HTTP_200_OK,
        )

    lang = user.language
    PasswordResetCode.objects.filter(user=user, is_used=False).update(is_used=True)
    reset = PasswordResetCode.objects.create(user=user)

    send_localized_mail(
        subject_ru=f"{APP_NAME} — Код для сброса пароля",
        subject_en=f"{APP_NAME} — Password reset code",
        message_ru=(
            f"Вы запросили сброс пароля.\n\n"
            f"Ваш код: {reset.code}\n\n"
            f"Введите его на сайте для установки нового пароля.\n"
            f"Код действителен 15 минут.\n\n"
            f"Если вы не запрашивали сброс — просто проигнорируйте это письмо.\n\n"
            f"— {APP_NAME}"
        ),
        message_en=(
            f"You requested a password reset.\n\n"
            f"Your code: {reset.code}\n\n"
            f"Enter this code on the site to set a new password.\n"
            f"The code expires in 15 minutes.\n\n"
            f"If you didn't request this, you can safely ignore this email.\n\n"
            f"— {APP_NAME}"
        ),
        recipient=email,
        lang=lang,
    )

    return Response(
        {"message": "If this email is registered, you will receive a reset code."},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([PasswordResetRateThrottle])
def verify_password_reset_code(request):
    email = request.data.get("email", "").lower()
    code = request.data.get("code", "")

    if not email or not code:
        return Response(
            {"error": "Email and code are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {"error": "Invalid or expired code."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    reset = (
        PasswordResetCode.objects.filter(user=user, is_used=False)
        .order_by("-created_at")
        .first()
    )

    if not reset or not reset.is_valid():
        return Response(
            {"error": "Invalid or expired code."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if reset.code != code:
        reset.max_attempts += 1
        if reset.max_attempts >= 5:
            reset.is_used = True
        reset.save(update_fields=["max_attempts", "is_used"])
        return Response(
            {"error": "Invalid or expired code."}, status=status.HTTP_400_BAD_REQUEST
        )

    return Response(
        {"message": "Code is valid."},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([PasswordResetRateThrottle])
def confirm_password_reset(request):
    serializer = ConfirmPasswordResetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data["email"]
    code = serializer.validated_data["code"]
    new_password = serializer.validated_data["new_password"]

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {"error": "Invalid or expired code."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    reset = (
        PasswordResetCode.objects.filter(user=user, code=code, is_used=False)
        .order_by("-created_at")
        .first()
    )

    if not reset or not reset.is_valid():
        return Response(
            {"error": "Invalid or expired code."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    lang = user.language
    user.set_password(new_password)
    user.save()

    reset.is_used = True
    reset.save(update_fields=["is_used"])

    send_localized_mail(
        subject_ru=f"{APP_NAME} — Пароль изменён",
        subject_en=f"{APP_NAME} — Your password has been changed",
        message_ru=(
            f"Ваш пароль был успешно изменён.\n\n"
            f"— {APP_NAME}"
        ),
        message_en=(
            f"Your password was successfully reset.\n\n"
            f"— {APP_NAME}"
        ),
        recipient=email,
        lang=lang,
    )

    return Response(
        {"message": "Password has been reset successfully. You can now log in."},
        status=status.HTTP_200_OK,
    )
