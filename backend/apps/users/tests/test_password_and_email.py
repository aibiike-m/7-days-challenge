import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from apps.users.models import EmailVerification
from unittest.mock import patch

User = get_user_model()

@pytest.mark.django_db
class TestDisplayName:
    def test_user_default_display_name(self, faker):
        user = User.objects.create_user(email=faker.email(), password="pass123")
        assert user.display_name == "User"

    def test_update_display_name(self, auth_client, test_user):
        url = "/api/users/me/"
        response = auth_client.patch(url, {"display_name": "Alice"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["display_name"] == "Alice"
        test_user.refresh_from_db()
        assert test_user.display_name == "Alice"

    def test_display_name_not_unique(self, faker):
        user1 = User.objects.create_user(email=faker.email(), password="pass")
        user2 = User.objects.create_user(email=faker.email(), password="pass")
        user1.display_name = "Alice"
        user2.display_name = "Alice"
        user1.save()
        user2.save()
        assert user1.display_name == user2.display_name == "Alice"

    def test_username_is_unique(self, faker):
        user1 = User.objects.create_user(email=faker.email(), password="pass")
        user2 = User.objects.create_user(email=faker.email(), password="pass")
        assert user1.username != user2.username

@pytest.mark.django_db
class TestPasswordManagement:
    def test_has_password_endpoint(self, auth_client):
        url = "/api/users/has-password/"
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "has_password" in response.data
        assert response.data["has_password"] is True

    def test_change_password_success(self, auth_client, test_user):
        url = "/api/users/change-password/"
        data = {
            "old_password": "testpass123",
            "new_password": "newstrongpass456",
            "confirm_password": "newstrongpass456",
        }
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        test_user.refresh_from_db()
        assert test_user.check_password("newstrongpass456")

    def test_change_password_wrong_old_password(self, auth_client):
        url = "/api/users/change-password/"
        data = {
            "old_password": "wrongpassword",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        }
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "old_password" in str(response.data).lower()

    def test_change_password_mismatch(self, auth_client):
        url = "/api/users/change-password/"
        data = {
            "old_password": "testpass123",
            "new_password": "newpass123",
            "confirm_password": "different456",
        }
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_set_password_for_google_user(self, api_client, faker):
        user = User.objects.create(email=faker.email(), language="en")
        user.set_unusable_password()
        user.save()
        api_client.force_authenticate(user=user)
        url_check = "/api/users/has-password/"
        response = api_client.get(url_check)
        assert response.data["has_password"] is False
        url = "/api/users/set-password/"
        data = {
            "new_password": "newpassword123",
            "confirm_password": "newpassword123",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password("newpassword123")

    def test_set_password_when_already_has_password(self, auth_client):
        url = "/api/users/set-password/"
        data = {
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        }
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestEmailChange:
    @patch("apps.users.views.send_mail")
    def test_request_email_change_success(self, mock_send_mail, auth_client, faker):
        new_email = faker.email()
        url = "/api/users/request-email-change/"
        data = {"new_email": new_email}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        verification = EmailVerification.objects.filter(
            user=auth_client.user, new_email=new_email
        ).first()
        assert verification is not None
        assert len(verification.code) == 6
        assert verification.is_used is False
        mock_send_mail.assert_called_once()

    def test_request_email_change_same_email(self, auth_client, test_user):
        url = "/api/users/request-email-change/"
        data = {"new_email": test_user.email}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_request_email_change_existing_email(self, auth_client, faker):
        existing_user = User.objects.create_user(
            email=faker.email(), password="pass123"
        )
        url = "/api/users/request-email-change/"
        data = {"new_email": existing_user.email}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("apps.users.views.send_mail")
    def test_confirm_email_change_success(
        self, mock_send_mail, auth_client, test_user, faker
    ):
        new_email = faker.email()
        verification = EmailVerification.objects.create(
            user=test_user, new_email=new_email
        )
        url = "/api/users/confirm-email-change/"
        data = {"code": verification.code}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["new_email"] == new_email
        test_user.refresh_from_db()
        assert test_user.email == new_email
        verification.refresh_from_db()
        assert verification.is_used is True

    def test_confirm_email_change_invalid_code(self, auth_client):
        url = "/api/users/confirm-email-change/"
        data = {"code": "000000"}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("apps.users.views.send_mail")
    def test_confirm_email_change_expired_code(
        self, mock_send_mail, auth_client, test_user, faker
    ):
        from datetime import timedelta
        from django.utils import timezone
        new_email = faker.email()
        verification = EmailVerification.objects.create(
            user=test_user, new_email=new_email
        )
        verification.expires_at = timezone.now() - timedelta(minutes=1)
        verification.save()
        url = "/api/users/confirm-email-change/"
        data = {"code": verification.code}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "expired" in str(response.data).lower()
            or "истек" in str(response.data).lower()
        )

    @patch("apps.users.views.send_mail")
    def test_confirm_email_change_already_used_code(
        self, mock_send_mail, auth_client, test_user, faker
    ):
        new_email = faker.email()
        verification = EmailVerification.objects.create(
            user=test_user, new_email=new_email, is_used=True
        )
        url = "/api/users/confirm-email-change/"
        data = {"code": verification.code}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestEmailVerificationModel:
    def test_code_auto_generation(self, test_user, faker):
        verification = EmailVerification.objects.create(
            user=test_user, new_email=faker.email()
        )
        assert verification.code is not None
        assert len(verification.code) == 6
        assert verification.code.isdigit()

    def test_expires_at_auto_set(self, test_user, faker):
        from django.utils import timezone
        from datetime import timedelta
        before = timezone.now()
        verification = EmailVerification.objects.create(
            user=test_user, new_email=faker.email()
        )
        after = timezone.now()
        expected_time = before + timedelta(minutes=15)
        assert verification.expires_at >= expected_time - timedelta(seconds=5)
        assert verification.expires_at <= after + timedelta(minutes=15, seconds=5)

    def test_is_valid_method(self, test_user, faker):
        from django.utils import timezone
        from datetime import timedelta
        valid = EmailVerification.objects.create(
            user=test_user, new_email=faker.email()
        )
        assert valid.is_valid() is True
        used = EmailVerification.objects.create(
            user=test_user, new_email=faker.email(), is_used=True
        )
        assert used.is_valid() is False
        expired = EmailVerification.objects.create(
            user=test_user, new_email=faker.email()
        )
        expired.expires_at = timezone.now() - timedelta(minutes=1)
        expired.save()
        assert expired.is_valid() is False

@pytest.mark.django_db
class TestIntegrationScenarios:
    def test_full_user_journey_with_password_and_email_change(self, api_client, faker):
        email = faker.email()
        password = "initialpass123"
        register_data = {
            "email": email,
            "password": password,
            "re_password": password,
        }
        response = api_client.post("/api/auth/users/", register_data)
        assert response.status_code == status.HTTP_201_CREATED
        login_data = {"email": email, "password": password}
        response = api_client.post("/api/auth/login-by-email/", login_data)
        assert response.status_code == status.HTTP_200_OK
        user = User.objects.get(email=email)
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/users/me/")
        assert response.data["display_name"] == "User"
        response = api_client.patch("/api/users/me/", {"display_name": "John"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["display_name"] == "John"
        new_password = "newstrongpass456"
        password_data = {
            "old_password": password,
            "new_password": new_password,
            "confirm_password": new_password,
        }
        response = api_client.post("/api/users/change-password/", password_data)
        assert response.status_code == status.HTTP_200_OK
        api_client.force_authenticate(user=None)
        login_data = {"email": email, "password": new_password}
        response = api_client.post("/api/auth/login-by-email/", login_data)
        assert response.status_code == status.HTTP_200_OK

    @patch("apps.users.views.send_mail")
    def test_google_user_sets_password_and_changes_email(
        self, mock_send_mail, api_client, faker
    ):
        user = User.objects.create(email=faker.email(), language="en")
        user.set_unusable_password()
        user.save()
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/users/has-password/")
        assert response.data["has_password"] is False
        password = "newsecurepass123"
        set_pass_data = {
            "new_password": password,
            "confirm_password": password,
        }
        response = api_client.post("/api/users/set-password/", set_pass_data)
        assert response.status_code == status.HTTP_200_OK
        response = api_client.get("/api/users/has-password/")
        assert response.data["has_password"] is True
        new_email = faker.email()
        response = api_client.post(
            "/api/users/request-email-change/", {"new_email": new_email}
        )
        assert response.status_code == status.HTTP_200_OK
        verification = EmailVerification.objects.filter(user=user).first()
        response = api_client.post(
            "/api/users/confirm-email-change/", {"code": verification.code}
        )
        assert response.status_code == status.HTTP_200_OK
        api_client.force_authenticate(user=None)
        response = api_client.post(
            "/api/auth/login-by-email/", {"email": new_email, "password": password}
        )
        assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
class TestGoogleOAuthPasswordHandling:
    @patch("apps.users.social_views.id_token.verify_oauth2_token")
    def test_new_google_user_has_no_usable_password(
        self, mock_verify, api_client, faker
    ):
        email = faker.email()
        mock_verify.return_value = {"email": email, "sub": "google123"}
        url = "/api/auth/google/"
        data = {"credential": "fake_google_token", "language": "en"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["created"] is True
        user = User.objects.get(email=email)
        assert user.has_usable_password() is False
        assert user.password.startswith("!")

    @patch("apps.users.social_views.id_token.verify_oauth2_token")
    def test_google_user_password_field_format(self, mock_verify, api_client, faker):
        email = faker.email()
        mock_verify.return_value = {"email": email, "sub": "google456"}
        url = "/api/auth/google/"
        data = {"credential": "fake_token", "language": "en"}
        api_client.post(url, data)
        user = User.objects.get(email=email)
        assert user.password != ""
        assert user.password.startswith("!")
        assert len(user.password) > 1

    @patch("apps.users.social_views.id_token.verify_oauth2_token")
    def test_google_user_api_returns_no_password(self, mock_verify, api_client, faker):
        email = faker.email()
        mock_verify.return_value = {"email": email, "sub": "google789"}
        url = "/api/auth/google/"
        data = {"credential": "fake_token", "language": "en"}
        response = api_client.post(url, data)
        user = User.objects.get(email=email)
        api_client.force_authenticate(user=user)
        url = "/api/users/has-password/"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["has_password"] is False

    @patch("apps.users.social_views.id_token.verify_oauth2_token")
    def test_google_user_cannot_change_password_without_setting_first(
        self, mock_verify, api_client, faker
    ):
        email = faker.email()
        mock_verify.return_value = {"email": email, "sub": "google999"}
        url = "/api/auth/google/"
        api_client.post(url, {"credential": "fake_token", "language": "en"})
        user = User.objects.get(email=email)
        api_client.force_authenticate(user=user)
        url = "/api/users/change-password/"
        data = {
            "old_password": "anything",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert "password" in response.data["error"].lower()
        assert "set" in response.data["error"].lower()
        
    @patch("apps.users.social_views.id_token.verify_oauth2_token")
    def test_google_user_can_set_password(self, mock_verify, api_client, faker):
        email = faker.email()
        mock_verify.return_value = {"email": email, "sub": "google111"}
        url = "/api/auth/google/"
        api_client.post(url, {"credential": "fake_token", "language": "en"})
        user = User.objects.get(email=email)
        api_client.force_authenticate(user=user)
        assert user.has_usable_password() is False
        url = "/api/users/set-password/"
        data = {
            "new_password": "mynewpass123",
            "confirm_password": "mynewpass123",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.has_usable_password() is True
        assert user.check_password("mynewpass123") is True

    @patch("apps.users.social_views.id_token.verify_oauth2_token")
    def test_google_user_full_flow_set_then_change_password(
        self, mock_verify, api_client, faker
    ):
        email = faker.email()
        mock_verify.return_value = {"email": email, "sub": "google222"}
        url = "/api/auth/google/"
        api_client.post(url, {"credential": "token", "language": "en"})
        user = User.objects.get(email=email)
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/users/has-password/")
        assert response.data["has_password"] is False
        url = "/api/users/set-password/"
        api_client.post(
            url,
            {
                "new_password": "firstpass123",
                "confirm_password": "firstpass123",
            },
        )
        user.refresh_from_db()
        assert user.has_usable_password() is True
        response = api_client.get("/api/users/has-password/")
        assert response.data["has_password"] is True
        url = "/api/users/change-password/"
        response = api_client.post(
            url,
            {
                "old_password": "firstpass123",
                "new_password": "secondpass456",
                "confirm_password": "secondpass456",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password("secondpass456") is True
        assert user.check_password("firstpass123") is False

    def test_comparison_google_vs_normal_user_password_format(self, faker):
        google_user = User.objects.create(email=faker.email(), language="en")
        google_user.set_unusable_password()
        google_user.save()
        normal_user = User.objects.create_user(email=faker.email(), password="testpass123")
        assert google_user.password.startswith("!")
        assert not normal_user.password.startswith("!")
        assert "$" in normal_user.password
        assert len(normal_user.password) > 20
        assert google_user.has_usable_password() is False
        assert normal_user.has_usable_password() is True

    def test_empty_password_vs_unusable_password(self, faker):
        wrong_user = User.objects.create(email=faker.email())
        correct_user = User.objects.create(email=faker.email())
        correct_user.set_unusable_password()
        correct_user.save()
        assert correct_user.has_usable_password() is False
        assert correct_user.password.startswith("!")

    @patch("apps.users.social_views.id_token.verify_oauth2_token")
    def test_existing_google_user_login_preserves_no_password_state(
        self, mock_verify, api_client, faker
    ):
        email = faker.email()
        mock_verify.return_value = {"email": email, "sub": "google333"}
        url = "/api/auth/google/"
        api_client.post(url, {"credential": "token1", "language": "en"})
        user = User.objects.get(email=email)
        assert user.has_usable_password() is False
        response = api_client.post(url, {"credential": "token2", "language": "ru"})
        assert response.data["created"] is False
        user.refresh_from_db()
        assert user.has_usable_password() is False
        assert user.password.startswith("!")
