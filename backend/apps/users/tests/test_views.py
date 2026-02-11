import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from unittest.mock import patch

User = get_user_model()


@pytest.mark.django_db
class TestAuthenticationAPI:

    def test_register_user(self, api_client, faker):
        url = "/api/auth/users/"
        email = faker.email()
        password = faker.password(length=12)
        data = {
            "email": email,
            "password": password,
            "re_password": password,
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email=email).exists()

    def test_register_duplicate_email(self, api_client, test_user, faker):
        url = "/api/auth/users/"
        password = faker.password(length=12)
        data = {
            "email": test_user.email,
            "password": password,
            "re_password": password,
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_with_valid_credentials(self, api_client, test_user):
        url = "/api/auth/login-by-email/"
        data = {"email": test_user.email, "password": "testpass123"}

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user"]["email"] == test_user.email

    def test_login_with_invalid_credentials(self, api_client, test_user):
        url = "/api/auth/login-by-email/"
        data = {"email": test_user.email, "password": "wrongpassword"}

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_without_email(self, api_client):
        url = "/api/auth/login-by-email/"
        data = {"password": "testpass123"}

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_non_existent_email(self, api_client, faker):
        url = "/api/auth/login-by-email/"
        data = {"email": faker.email(), "password": "testpass123"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid credentials" in str(response.data).lower()

    def test_register_passwords_do_not_match(self, api_client, faker):
        url = "/api/auth/users/"
        email = faker.email()
        data = {
            "email": email,
            "password": "StrongPass123!",
            "re_password": "DifferentPass456!",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data
        assert "didn't match" in str(response.data["non_field_errors"]).lower()


@pytest.mark.django_db
class TestGoogleOAuth:

    @patch("apps.users.social_views.id_token.verify_oauth2_token")
    def test_google_login_new_user(self, mock_verify, api_client, faker):
        email = faker.email()
        mock_verify.return_value = {"email": email, "sub": "12345"}

        url = "/api/auth/google/"
        data = {"credential": "fake_token", "language": "en"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["created"] is True
        assert User.objects.filter(email=email).exists()

    @patch("apps.users.social_views.id_token.verify_oauth2_token")
    def test_google_login_existing_user(self, mock_verify, api_client, test_user):
        mock_verify.return_value = {"email": test_user.email, "sub": "67890"}

        url = "/api/auth/google/"
        data = {"credential": "fake_token", "language": "ru"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["created"] is False

        test_user.refresh_from_db()
        assert test_user.language == "ru"

    @patch("apps.users.social_views.id_token.verify_oauth2_token")
    def test_google_login_invalid_token(self, mock_verify, api_client):
        mock_verify.side_effect = ValueError("Invalid token")

        url = "/api/auth/google/"
        data = {"credential": "invalid_token", "language": "en"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST



    @patch("apps.users.social_views.id_token.verify_oauth2_token")
    def test_google_login_no_credential(self, mock_verify, api_client):
        url = "/api/auth/google/"
        data = {"language": "en"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Token not provided" in response.data["error"]

    @patch("apps.users.social_views.id_token.verify_oauth2_token")
    def test_google_login_no_email_in_token(self, mock_verify, api_client):
        mock_verify.return_value = {"sub": "12345"}
        url = "/api/auth/google/"
        data = {"credential": "fake_token"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email not found" in response.data["error"]


@pytest.mark.django_db
class TestUserViewSet:

    def test_get_current_user(self, auth_client, test_user):
        url = "/api/users/me/"
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == test_user.email
        assert response.data["language"] == test_user.language

    def test_update_user_language(self, auth_client, test_user):
        url = "/api/users/me/"
        response = auth_client.patch(url, {"language": "ru"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["language"] == "ru"

        test_user.refresh_from_db()
        assert test_user.language == "ru"

    def test_cannot_update_email(self, auth_client, test_user, faker):
        url = "/api/users/me/"
        new_email = faker.email()
        response = auth_client.patch(url, {"email": new_email})

        assert response.status_code == status.HTTP_200_OK

        test_user.refresh_from_db()
        assert test_user.email != new_email

    def test_unauthenticated_user_cannot_access(self, api_client):
        url = "/api/users/me/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    
    def test_weekly_stats_empty_week(self, auth_client):
        url = "/api/users/stats/weekly/"
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 7
        assert all(item["percent"] == 0 for item in response.data)

    @pytest.mark.django_db(transaction=True)
    def test_weekly_stats_with_data(self, auth_client, test_user):
        from apps.challenges.models import Challenge, Task
        from datetime import date, timedelta
        today = date.today()
        weekday = today.weekday()
        start_of_week = today - timedelta(days=weekday)

        challenge = Challenge.objects.create(
            user=test_user,
            start_date=start_of_week,
            status="active"
        )

        Task.objects.create(challenge=challenge, day_number=1, is_completed=True)
        Task.objects.create(challenge=challenge, day_number=3, is_completed=False)

        url = "/api/users/stats/weekly/"
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        stats = response.data

        assert stats[0]["percent"] == 100
        assert stats[2]["percent"] == 0
        assert all(s["percent"] == 0 for i, s in enumerate(stats) if i not in [0, 2])


@pytest.mark.django_db
class TestLogout:

    def test_logout_blacklists_token(self, auth_client):
        url_login = "/api/auth/login-by-email/"
        login_data = {"email": auth_client.user.email, "password": "testpass123"}
        login_resp = auth_client.post(url_login, login_data)
        refresh = login_resp.data["refresh"]

        url_logout = "/api/logout/"
        data = {"refresh": refresh}
        response = auth_client.post(url_logout, data)

        assert response.status_code == status.HTTP_200_OK
        assert "Logged out successfully" in response.data["message"]

        from rest_framework_simplejwt.tokens import RefreshToken

        try:
            token = RefreshToken(refresh)
            token.check_blacklist()
            assert False, "Token should be blacklisted"
        except:
            assert True

    def test_logout_without_token(self, auth_client):
        url = "/api/logout/"
        response = auth_client.post(url, {})
        assert response.status_code == status.HTTP_200_OK
