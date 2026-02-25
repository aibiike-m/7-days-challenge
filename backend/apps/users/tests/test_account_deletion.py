import uuid
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import AccountDeletion

User = get_user_model()


@pytest.mark.django_db
class TestDeleteAccountWithPassword:
    @patch("apps.users.views.send_mail")
    def test_delete_account_success(self, mock_send_mail, auth_client, test_user):
        user_id = test_user.id
        url = "/api/users/delete-account/"
        response = auth_client.post(url, {"password": "testpass123"})

        assert response.status_code == status.HTTP_200_OK
        assert "deleted" in response.data["message"].lower()
        assert not User.objects.filter(id=user_id).exists()

    @patch("apps.users.views.send_mail")
    def test_delete_account_sends_confirmation_email(
        self, mock_send_mail, auth_client, test_user
    ):
        email = test_user.email
        auth_client.post("/api/users/delete-account/", {"password": "testpass123"})

        mock_send_mail.assert_called_once()
        _, kwargs = mock_send_mail.call_args
        assert email in kwargs["recipient_list"]

    def test_delete_account_wrong_password(self, auth_client):
        url = "/api/users/delete-account/"
        response = auth_client.post(url, {"password": "wrongpassword"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert User.objects.filter(id=auth_client.user.id).exists()

    def test_delete_account_missing_password_field(self, auth_client):
        url = "/api/users/delete-account/"
        response = auth_client.post(url, {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert User.objects.filter(id=auth_client.user.id).exists()

    def test_delete_account_requires_authentication(self, api_client):
        url = "/api/users/delete-account/"
        response = api_client.post(url, {"password": "testpass123"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestDeleteAccountOAuth:
    @patch("apps.users.views.send_mail")
    def test_delete_account_sends_email_link(
        self, mock_send_mail, oauth_client, oauth_user
    ):
        url = "/api/users/delete-account/"
        response = oauth_client.post(url, {})

        assert response.status_code == status.HTTP_200_OK
        assert "email" in response.data["message"].lower()
        mock_send_mail.assert_called_once()
        assert User.objects.filter(id=oauth_user.id).exists()

    @patch("apps.users.views.send_mail")
    def test_delete_account_creates_deletion_token(
        self, mock_send_mail, oauth_client, oauth_user
    ):
        oauth_client.post("/api/users/delete-account/", {})

        deletion = AccountDeletion.objects.filter(
            user=oauth_user, is_used=False
        ).first()
        assert deletion is not None
        assert deletion.is_valid()

    @patch("apps.users.views.send_mail")
    def test_new_request_invalidates_previous_token(
        self, mock_send_mail, oauth_client, oauth_user
    ):
        oauth_client.post("/api/users/delete-account/", {})
        old_deletion = AccountDeletion.objects.filter(user=oauth_user).first()
        old_token = old_deletion.token

        oauth_client.post("/api/users/delete-account/", {})

        old_deletion.refresh_from_db()
        assert old_deletion.is_used is True

        new_deletion = AccountDeletion.objects.filter(
            user=oauth_user, is_used=False
        ).first()
        assert new_deletion is not None
        assert new_deletion.token != old_token


@pytest.mark.django_db
class TestConfirmDeleteAccount:
    @patch("apps.users.views.send_mail")
    def test_confirm_deletion_deletes_user(
        self, mock_send_mail, oauth_user, api_client
    ):
        deletion = AccountDeletion.objects.create(user=oauth_user)
        user_id = oauth_user.id

        url = f"/api/users/confirm-account-deletion/?token={deletion.token}"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert not User.objects.filter(id=user_id).exists()

    @patch("apps.users.views.send_mail")
    def test_confirm_deletion_sends_notification_email(
        self, mock_send_mail, oauth_user, api_client
    ):
        email = oauth_user.email
        deletion = AccountDeletion.objects.create(user=oauth_user)

        api_client.get(f"/api/users/confirm-account-deletion/?token={deletion.token}")

        mock_send_mail.assert_called_once()
        _, kwargs = mock_send_mail.call_args
        assert email in kwargs["recipient_list"]

    @patch("apps.users.views.send_mail")
    def test_confirm_deletion_marks_token_as_used(
        self, mock_send_mail, oauth_user, api_client
    ):
        deletion = AccountDeletion.objects.create(user=oauth_user)
        token = deletion.token

        api_client.get(f"/api/users/confirm-account-deletion/?token={token}")

        assert not AccountDeletion.objects.filter(token=token).exists()

    def test_confirm_deletion_does_not_require_authentication(
        self, oauth_user, api_client
    ):
        deletion = AccountDeletion.objects.create(user=oauth_user)
        unauthenticated = APIClient()

        with patch("apps.users.views.send_mail"):
            response = unauthenticated.get(
                f"/api/users/confirm-account-deletion/?token={deletion.token}"
            )

        assert response.status_code == status.HTTP_200_OK

    def test_confirm_deletion_invalid_token(self, api_client):
        url = f"/api/users/confirm-account-deletion/?token={uuid.uuid4()}"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_confirm_deletion_without_token(self, api_client):
        url = "/api/users/confirm-account-deletion/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_confirm_deletion_expired_token(self, oauth_user, api_client):
        deletion = AccountDeletion.objects.create(user=oauth_user)
        deletion.expires_at = timezone.now() - timedelta(hours=2)
        deletion.save()

        url = f"/api/users/confirm-account-deletion/?token={deletion.token}"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "expired" in str(response.data).lower()
        assert User.objects.filter(id=oauth_user.id).exists()

    def test_confirm_deletion_already_used_token(self, oauth_user, api_client):
        deletion = AccountDeletion.objects.create(user=oauth_user, is_used=True)

        url = f"/api/users/confirm-account-deletion/?token={deletion.token}"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("apps.users.views.send_mail")
    def test_token_cannot_be_reused_after_deletion(
        self, mock_send_mail, oauth_user, api_client
    ):
        deletion = AccountDeletion.objects.create(user=oauth_user)
        token = deletion.token

        api_client.get(f"/api/users/confirm-account-deletion/?token={token}")

        response = api_client.get(f"/api/users/confirm-account-deletion/?token={token}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
