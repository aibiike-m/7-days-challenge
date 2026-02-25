from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from apps.users.models import EmailVerification

User = get_user_model() 


@ pytest.mark.django_db
class TestIntegrationScenarios:
    def test_full_user_journey_with_password_and_email_change(self, api_client, faker):
        email = faker.email()
        password = "initialpass123"
        response = api_client.post(
            "/api/auth/users/",
            {"email": email, "password": password, "re_password": password},
        )
        assert response.status_code == status.HTTP_201_CREATED
        response = api_client.post(
            "/api/auth/login-by-email/", {"email": email, "password": password}
        )
        assert response.status_code == status.HTTP_200_OK
        user = User.objects.get(email=email)
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/users/me/")
        assert response.data["display_name"] == "User"
        response = api_client.patch("/api/users/me/", {"display_name": "John"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["display_name"] == "John"
        new_password = "newstrongpass456"
        response = api_client.post(
            "/api/users/change-password/",
            {
                "old_password": password,
                "new_password": new_password,
                "confirm_password": new_password,
            },
        )
        assert response.status_code == status.HTTP_200_OK
        api_client.force_authenticate(user=None)
        response = api_client.post(
            "/api/auth/login-by-email/", {"email": email, "password": new_password}
        )
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
        response = api_client.post(
            "/api/users/set-password/",
            {"new_password": password, "confirm_password": password},
        )
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
