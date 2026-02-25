import pytest
from datetime import timedelta
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import PasswordResetCode

User = get_user_model()


@pytest.mark.django_db
class TestRequestPasswordReset:
    @patch("apps.users.views.send_mail")
    def test_sends_code_for_existing_user(self, mock_send_mail, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="pass123")
        response = api_client.post(
            "/api/auth/request-password-reset/",
            {"email": user.email},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        assert PasswordResetCode.objects.filter(user=user, is_used=False).exists()
        mock_send_mail.assert_called_once()

    @patch("apps.users.views.send_mail")
    def test_code_sent_to_correct_email(self, mock_send_mail, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="pass123")
        api_client.post(
            "/api/auth/request-password-reset/",
            {"email": user.email},
        )
        _, kwargs = mock_send_mail.call_args
        assert user.email in kwargs["recipient_list"]

    def test_returns_200_for_nonexistent_email(self, api_client, faker):
        response = api_client.post(
            "/api/auth/request-password-reset/",
            {"email": faker.email()},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data

    @patch("apps.users.views.send_mail")
    def test_does_not_send_mail_for_nonexistent_email(
        self, mock_send_mail, api_client, faker
    ):
        api_client.post(
            "/api/auth/request-password-reset/",
            {"email": faker.email()},
        )
        mock_send_mail.assert_not_called()

    @patch("apps.users.views.send_mail")
    def test_returns_200_for_google_user(self, mock_send_mail, api_client, faker):
        user = User.objects.create(email=faker.email())
        user.set_unusable_password()
        user.save()
        response = api_client.post(
            "/api/auth/request-password-reset/",
            {"email": user.email},
        )
        assert response.status_code == status.HTTP_200_OK
        mock_send_mail.assert_not_called()

    @patch("apps.users.views.send_mail")
    def test_invalidates_previous_codes(self, mock_send_mail, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="pass123")
        old_code = PasswordResetCode.objects.create(user=user)
        assert old_code.is_used is False

        api_client.post(
            "/api/auth/request-password-reset/",
            {"email": user.email},
        )

        old_code.refresh_from_db()
        assert old_code.is_used is True

    @patch("apps.users.views.send_mail")
    def test_only_one_active_code_at_a_time(self, mock_send_mail, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="pass123")
        api_client.post("/api/auth/request-password-reset/", {"email": user.email})
        api_client.post("/api/auth/request-password-reset/", {"email": user.email})
        api_client.post("/api/auth/request-password-reset/", {"email": user.email})

        active = PasswordResetCode.objects.filter(user=user, is_used=False)
        assert active.count() == 1

    def test_does_not_require_authentication(self, api_client, faker):
        unauthenticated = APIClient()
        user = User.objects.create_user(email=faker.email(), password="pass123")
        with patch("apps.users.views.send_mail"):
            response = unauthenticated.post(
                "/api/auth/request-password-reset/",
                {"email": user.email},
            )
        assert response.status_code == status.HTTP_200_OK

    def test_missing_email_field(self, api_client):
        response = api_client.post("/api/auth/request-password-reset/", {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_email_format(self, api_client):
        response = api_client.post(
            "/api/auth/request-password-reset/",
            {"email": "not-an-email"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("apps.users.views.send_mail")
    def test_generated_code_is_6_digits(self, mock_send_mail, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="pass123")
        api_client.post("/api/auth/request-password-reset/", {"email": user.email})
        code = PasswordResetCode.objects.filter(user=user, is_used=False).first()
        assert code is not None
        assert len(code.code) == 6
        assert code.code.isdigit()

    @patch("apps.users.views.send_mail")
    def test_code_expires_in_15_minutes(self, mock_send_mail, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="pass123")
        api_client.post("/api/auth/request-password-reset/", {"email": user.email})
        code = PasswordResetCode.objects.filter(user=user, is_used=False).first()
        assert code is not None
        delta = code.expires_at - timezone.now()
        assert timedelta(minutes=14) < delta < timedelta(minutes=16)


@pytest.mark.django_db
class TestConfirmPasswordReset:
    @patch("apps.users.views.send_mail")
    def test_reset_success(self, mock_send_mail, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="oldpass123")
        reset = PasswordResetCode.objects.create(user=user)

        response = api_client.post(
            "/api/auth/confirm-password-reset/",
            {
                "email": user.email,
                "code": reset.code,
                "new_password": "brandnewpass456",
                "confirm_password": "brandnewpass456",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        user.refresh_from_db()
        assert user.check_password("brandnewpass456")

    @patch("apps.users.views.send_mail")
    def test_marks_code_as_used_after_reset(self, mock_send_mail, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="oldpass123")
        reset = PasswordResetCode.objects.create(user=user)

        api_client.post(
            "/api/auth/confirm-password-reset/",
            {
                "email": user.email,
                "code": reset.code,
                "new_password": "brandnewpass456",
                "confirm_password": "brandnewpass456",
            },
        )
        reset.refresh_from_db()
        assert reset.is_used is True

    @patch("apps.users.views.send_mail")
    def test_sends_notification_email_after_reset(
        self, mock_send_mail, api_client, faker
    ):
        user = User.objects.create_user(email=faker.email(), password="oldpass123")
        reset = PasswordResetCode.objects.create(user=user)

        api_client.post(
            "/api/auth/confirm-password-reset/",
            {
                "email": user.email,
                "code": reset.code,
                "new_password": "brandnewpass456",
                "confirm_password": "brandnewpass456",
            },
        )
        mock_send_mail.assert_called_once()
        _, kwargs = mock_send_mail.call_args
        assert user.email in kwargs["recipient_list"]

    def test_wrong_code_returns_400(self, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="oldpass123")
        PasswordResetCode.objects.create(user=user)

        response = api_client.post(
            "/api/auth/confirm-password-reset/",
            {
                "email": user.email,
                "code": "000000",
                "new_password": "brandnewpass456",
                "confirm_password": "brandnewpass456",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        user.refresh_from_db()
        assert user.check_password("oldpass123")

    def test_expired_code_returns_400(self, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="oldpass123")
        reset = PasswordResetCode.objects.create(user=user)
        reset.expires_at = timezone.now() - timedelta(minutes=1)
        reset.save()

        response = api_client.post(
            "/api/auth/confirm-password-reset/",
            {
                "email": user.email,
                "code": reset.code,
                "new_password": "brandnewpass456",
                "confirm_password": "brandnewpass456",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        user.refresh_from_db()
        assert user.check_password("oldpass123")

    def test_already_used_code_returns_400(self, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="oldpass123")
        reset = PasswordResetCode.objects.create(user=user, is_used=True)

        response = api_client.post(
            "/api/auth/confirm-password-reset/",
            {
                "email": user.email,
                "code": reset.code,
                "new_password": "brandnewpass456",
                "confirm_password": "brandnewpass456",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_nonexistent_email_returns_400(self, api_client, faker):
        response = api_client.post(
            "/api/auth/confirm-password-reset/",
            {
                "email": faker.email(),
                "code": "123456",
                "new_password": "brandnewpass456",
                "confirm_password": "brandnewpass456",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_passwords_mismatch_returns_400(self, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="oldpass123")
        reset = PasswordResetCode.objects.create(user=user)

        response = api_client.post(
            "/api/auth/confirm-password-reset/",
            {
                "email": user.email,
                "code": reset.code,
                "new_password": "brandnewpass456",
                "confirm_password": "differentpass789",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_code_cannot_be_reused(self, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="oldpass123")
        reset = PasswordResetCode.objects.create(user=user)

        payload = {
            "email": user.email,
            "code": reset.code,
            "new_password": "brandnewpass456",
            "confirm_password": "brandnewpass456",
        }

        with patch("apps.users.views.send_mail"):
            first = api_client.post("/api/auth/confirm-password-reset/", payload)
            second = api_client.post("/api/auth/confirm-password-reset/", payload)

        assert first.status_code == status.HTTP_200_OK
        assert second.status_code == status.HTTP_400_BAD_REQUEST

    def test_missing_fields_returns_400(self, api_client):
        response = api_client.post(
            "/api/auth/confirm-password-reset/",
            {"email": "test@example.com"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_does_not_require_authentication(self, api_client, faker):
        unauthenticated = APIClient()
        user = User.objects.create_user(email=faker.email(), password="oldpass123")
        reset = PasswordResetCode.objects.create(user=user)

        with patch("apps.users.views.send_mail"):
            response = unauthenticated.post(
                "/api/auth/confirm-password-reset/",
                {
                    "email": user.email,
                    "code": reset.code,
                    "new_password": "brandnewpass456",
                    "confirm_password": "brandnewpass456",
                },
            )
        assert response.status_code == status.HTTP_200_OK

    @patch("apps.users.views.send_mail")
    def test_can_login_with_new_password_after_reset(
        self, mock_send_mail, api_client, faker
    ):
        email = faker.email()
        user = User.objects.create_user(email=email, password="oldpass123")
        reset = PasswordResetCode.objects.create(user=user)

        api_client.post(
            "/api/auth/confirm-password-reset/",
            {
                "email": email,
                "code": reset.code,
                "new_password": "brandnewpass456",
                "confirm_password": "brandnewpass456",
            },
        )

        login_response = api_client.post(
            "/api/auth/login-by-email/",
            {"email": email, "password": "brandnewpass456"},
        )
        assert login_response.status_code == status.HTTP_200_OK
        assert "access" in login_response.data

    @patch("apps.users.views.send_mail")
    def test_old_password_does_not_work_after_reset(
        self, mock_send_mail, api_client, faker
    ):
        email = faker.email()
        user = User.objects.create_user(email=email, password="oldpass123")
        reset = PasswordResetCode.objects.create(user=user)

        api_client.post(
            "/api/auth/confirm-password-reset/",
            {
                "email": email,
                "code": reset.code,
                "new_password": "brandnewpass456",
                "confirm_password": "brandnewpass456",
            },
        )

        login_response = api_client.post(
            "/api/auth/login-by-email/",
            {"email": email, "password": "oldpass123"},
        )
        assert login_response.status_code == status.HTTP_401_UNAUTHORIZED
