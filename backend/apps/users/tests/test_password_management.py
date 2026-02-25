from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


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
        response = api_client.get("/api/users/has-password/")
        assert response.data["has_password"] is False
        data = {
            "new_password": "newpassword123",
            "confirm_password": "newpassword123",
        }
        response = api_client.post("/api/users/set-password/", data)
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
class TestGoogleOAuthPasswordHandling:

    @patch("apps.users.social_views.id_token.verify_oauth2_token")
    def test_new_google_user_has_no_usable_password(
        self, mock_verify, api_client, faker
    ):
        email = faker.email()
        mock_verify.return_value = {
            "email": email,
            "sub": "google123",
            "email_verified": True,
        }
        response = api_client.post(
            "/api/auth/google/", {"credential": "fake_google_token", "language": "en"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["created"] is True
        user = User.objects.get(email=email)
        assert user.has_usable_password() is False
        assert user.password.startswith("!")

    @patch("apps.users.social_views.id_token.verify_oauth2_token")
    def test_google_user_cannot_change_password_without_setting_first(
        self, mock_verify, api_client, faker
    ):
        email = faker.email()
        mock_verify.return_value = {
            "email": email,
            "sub": "google999",
            "email_verified": True,
        }
        api_client.post(
            "/api/auth/google/", {"credential": "fake_token", "language": "en"}
        )
        user = User.objects.get(email=email)
        api_client.force_authenticate(user=user)
        response = api_client.post(
            "/api/users/change-password/",
            {
                "old_password": "anything",
                "new_password": "newpass123",
                "confirm_password": "newpass123",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert "password" in response.data["error"].lower()

    @patch("apps.users.social_views.id_token.verify_oauth2_token")
    def test_google_user_can_set_password(self, mock_verify, api_client, faker):
        email = faker.email()
        mock_verify.return_value = {
            "email": email,
            "sub": "google111",
            "email_verified": True,
        }
        api_client.post(
            "/api/auth/google/", {"credential": "fake_token", "language": "en"}
        )
        user = User.objects.get(email=email)
        api_client.force_authenticate(user=user)
        response = api_client.post(
            "/api/users/set-password/",
            {"new_password": "mynewpass123", "confirm_password": "mynewpass123"},
        )
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.has_usable_password() is True
        assert user.check_password("mynewpass123") is True

    @patch("apps.users.social_views.id_token.verify_oauth2_token")
    def test_google_user_full_flow_set_then_change_password(
        self, mock_verify, api_client, faker
    ):
        email = faker.email()
        mock_verify.return_value = {
            "email": email,
            "sub": "google222",
            "email_verified": True,
        }
        api_client.post("/api/auth/google/", {"credential": "token", "language": "en"})
        user = User.objects.get(email=email)
        api_client.force_authenticate(user=user)
        api_client.post(
            "/api/users/set-password/",
            {"new_password": "firstpass123", "confirm_password": "firstpass123"},
        )
        user.refresh_from_db()
        assert user.has_usable_password() is True
        response = api_client.post(
            "/api/users/change-password/",
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

    @patch("apps.users.social_views.id_token.verify_oauth2_token")
    def test_existing_google_user_login_preserves_no_password_state(
        self, mock_verify, api_client, faker
    ):
        email = faker.email()
        mock_verify.return_value = {
            "email": email,
            "sub": "google333",
            "email_verified": True,
        }
        api_client.post("/api/auth/google/", {"credential": "token1", "language": "en"})
        user = User.objects.get(email=email)
        assert user.has_usable_password() is False
        response = api_client.post(
            "/api/auth/google/", {"credential": "token2", "language": "ru"}
        )
        assert response.data["created"] is False
        user.refresh_from_db()
        assert user.has_usable_password() is False
        assert user.password.startswith("!")
  