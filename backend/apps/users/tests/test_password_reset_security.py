import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework import status

from apps.users.models import PasswordResetCode

User = get_user_model()


@pytest.mark.django_db
class TestPasswordResetCodeVerification:
    @patch("apps.users.views.send_mail")
    def test_verify_valid_code_success(self, mock_send_mail, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="oldpass123")
        reset = PasswordResetCode.objects.create(user=user)

        response = api_client.post(
            "/api/auth/verify-password-reset-code/",
            {"email": user.email, "code": reset.code},
        )

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        reset.refresh_from_db()
        assert reset.is_used is False

    def test_verify_invalid_code_fails(self, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="oldpass123")
        PasswordResetCode.objects.create(user=user)

        response = api_client.post(
            "/api/auth/verify-password-reset-code/",
            {"email": user.email, "code": "000000"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_verify_expired_code_fails(self, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="oldpass123")
        reset = PasswordResetCode.objects.create(user=user)
        reset.expires_at = timezone.now() - timedelta(minutes=1)
        reset.save()

        response = api_client.post(
            "/api/auth/verify-password-reset-code/",
            {"email": user.email, "code": reset.code},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_used_code_fails(self, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="oldpass123")
        reset = PasswordResetCode.objects.create(user=user, is_used=True)

        response = api_client.post(
            "/api/auth/verify-password-reset-code/",
            {"email": user.email, "code": reset.code},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_code_nonexistent_email(self, api_client, faker):
        response = api_client.post(
            "/api/auth/verify-password-reset-code/",
            {"email": faker.email(), "code": "123456"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_code_missing_email(self, api_client):
        response = api_client.post(
            "/api/auth/verify-password-reset-code/",
            {"code": "123456"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_code_missing_code(self, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="oldpass123")

        response = api_client.post(
            "/api/auth/verify-password-reset-code/",
            {"email": user.email},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_code_does_not_mark_as_used(self, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="oldpass123")
        reset = PasswordResetCode.objects.create(user=user)

        api_client.post(
            "/api/auth/verify-password-reset-code/",
            {"email": user.email, "code": reset.code},
        )

        reset.refresh_from_db()
        assert reset.is_used is False
        assert reset.is_valid() is True


@pytest.mark.django_db
class TestPasswordResetSecurity:
    @patch("apps.users.views.send_mail")
    def test_cannot_reset_password_without_valid_code(
        self, mock_send_mail, api_client, faker
    ):
        user = User.objects.create_user(email=faker.email(), password="oldpass123")

        response = api_client.post(
            "/api/auth/confirm-password-reset/",
            {
                "email": user.email,
                "code": "000000",
                "new_password": "hackedpass456",
                "confirm_password": "hackedpass456",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        user.refresh_from_db()
        assert user.check_password("oldpass123")
        assert not user.check_password("hackedpass456")

    @patch("apps.users.views.send_mail")
    def test_code_must_be_checked_in_backend(self, mock_send_mail, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="oldpass123")
        reset = PasswordResetCode.objects.create(user=user)

        reset.is_used = True
        reset.save()

        response = api_client.post(
            "/api/auth/confirm-password-reset/",
            {
                "email": user.email,
                "code": reset.code,
                "new_password": "hackedpass456",
                "confirm_password": "hackedpass456",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        user.refresh_from_db()
        assert user.check_password("oldpass123")

    @patch("apps.users.views.send_mail")
    def test_expired_code_cannot_be_used(self, mock_send_mail, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="oldpass123")
        reset = PasswordResetCode.objects.create(user=user)

        reset.expires_at = timezone.now() - timedelta(minutes=1)
        reset.save()

        response = api_client.post(
            "/api/auth/confirm-password-reset/",
            {
                "email": user.email,
                "code": reset.code,
                "new_password": "hackedpass456",
                "confirm_password": "hackedpass456",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        user.refresh_from_db()
        assert user.check_password("oldpass123")

    @patch("apps.users.views.send_mail")
    def test_code_for_different_user_cannot_be_used(
        self, mock_send_mail, api_client, faker
    ):
        user1 = User.objects.create_user(email=faker.email(), password="user1pass")
        user2 = User.objects.create_user(email=faker.email(), password="user2pass")

        reset = PasswordResetCode.objects.create(user=user2)

        response = api_client.post(
            "/api/auth/confirm-password-reset/",
            {
                "email": user1.email,
                "code": reset.code,
                "new_password": "hackedpass456",
                "confirm_password": "hackedpass456",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        user1.refresh_from_db()
        user2.refresh_from_db()
        assert user1.check_password("user1pass")
        assert user2.check_password("user2pass")


@pytest.mark.django_db
class TestPasswordResetWeakPassword:
    @patch("apps.users.views.send_mail")
    def test_weak_password_returns_validation_error(
        self, mock_send_mail, api_client, faker
    ):
        user = User.objects.create_user(email=faker.email(), password="oldpass123")
        reset = PasswordResetCode.objects.create(user=user)

        response = api_client.post(
            "/api/auth/confirm-password-reset/",
            {
                "email": user.email,
                "code": reset.code,
                "new_password": "123",
                "confirm_password": "123",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "new_password" in response.data or "password" in str(response.data).lower()
        )

        user.refresh_from_db()
        assert user.check_password("oldpass123")

        reset.refresh_from_db()
        assert reset.is_used is False

    @patch("apps.users.views.send_mail")
    def test_numeric_only_password_rejected(self, mock_send_mail, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="oldpass123")
        reset = PasswordResetCode.objects.create(user=user)

        response = api_client.post(
            "/api/auth/confirm-password-reset/",
            {
                "email": user.email,
                "code": reset.code,
                "new_password": "12345678",
                "confirm_password": "12345678",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        user.refresh_from_db()
        assert user.check_password("oldpass123")

    @patch("apps.users.views.send_mail")
    def test_common_password_rejected(self, mock_send_mail, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="oldpass123")
        reset = PasswordResetCode.objects.create(user=user)

        response = api_client.post(
            "/api/auth/confirm-password-reset/",
            {
                "email": user.email,
                "code": reset.code,
                "new_password": "password",
                "confirm_password": "password",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("apps.users.views.send_mail")
    def test_strong_password_accepted(self, mock_send_mail, api_client, faker):
        user = User.objects.create_user(email=faker.email(), password="oldpass123")
        reset = PasswordResetCode.objects.create(user=user)

        response = api_client.post(
            "/api/auth/confirm-password-reset/",
            {
                "email": user.email,
                "code": reset.code,
                "new_password": "StrongP@ssw0rd!2024",
                "confirm_password": "StrongP@ssw0rd!2024",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password("StrongP@ssw0rd!2024")


@pytest.mark.django_db
class TestPasswordResetFullWorkflow:
    @patch("apps.users.views.send_mail")
    def test_full_password_reset_workflow(self, mock_send_mail, api_client, faker):
        email = faker.email()
        user = User.objects.create_user(email=email, password="oldpass123")

        response = api_client.post(
            "/api/auth/request-password-reset/",
            {"email": email},
        )
        assert response.status_code == status.HTTP_200_OK

        reset = PasswordResetCode.objects.filter(user=user).first()
        assert reset is not None

        response = api_client.post(
            "/api/auth/verify-password-reset-code/",
            {"email": email, "code": reset.code},
        )
        assert response.status_code == status.HTTP_200_OK

        response = api_client.post(
            "/api/auth/confirm-password-reset/",
            {
                "email": email,
                "code": reset.code,
                "new_password": "NewSecureP@ss456",
                "confirm_password": "NewSecureP@ss456",
            },
        )
        assert response.status_code == status.HTTP_200_OK

        login_response = api_client.post(
            "/api/auth/login-by-email/",
            {"email": email, "password": "NewSecureP@ss456"},
        )
        assert login_response.status_code == status.HTTP_200_OK
        assert "access" in login_response.data

        old_login = api_client.post(
            "/api/auth/login-by-email/",
            {"email": email, "password": "oldpass123"},
        )
        assert old_login.status_code == status.HTTP_401_UNAUTHORIZED

    @patch("apps.users.views.send_mail")
    def test_cannot_skip_code_verification_step(
        self, mock_send_mail, api_client, faker
    ):
        email = faker.email()
        user = User.objects.create_user(email=email, password="oldpass123")

        api_client.post("/api/auth/request-password-reset/", {"email": email})
        reset = PasswordResetCode.objects.filter(user=user).first()

        response = api_client.post(
            "/api/auth/confirm-password-reset/",
            {
                "email": email,
                "code": "999999",
                "new_password": "HackedP@ss456",
                "confirm_password": "HackedP@ss456",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        user.refresh_from_db()
        assert user.check_password("oldpass123")
        assert not user.check_password("HackedP@ss456")

    @patch("apps.users.views.send_mail")
    def test_verify_code_multiple_times_before_reset(
        self, mock_send_mail, api_client, faker
    ):
        email = faker.email()
        user = User.objects.create_user(email=email, password="oldpass123")

        api_client.post("/api/auth/request-password-reset/", {"email": email})
        reset = PasswordResetCode.objects.filter(user=user).first()

        for _ in range(3):
            response = api_client.post(
                "/api/auth/verify-password-reset-code/",
                {"email": email, "code": reset.code},
            )
            assert response.status_code == status.HTTP_200_OK

        reset.refresh_from_db()
        assert reset.is_used is False

        response = api_client.post(
            "/api/auth/confirm-password-reset/",
            {
                "email": email,
                "code": reset.code,
                "new_password": "NewP@ssw0rd456",
                "confirm_password": "NewP@ssw0rd456",
            },
        )
        assert response.status_code == status.HTTP_200_OK
