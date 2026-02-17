import uuid
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import AccountDeletion, EmailVerification, PasswordResetCode

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
        assert mock_send_mail.call_count == 2

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
class TestRequestEmailChangeSendsTwoEmails:
    @patch("apps.users.views.send_mail")
    def test_sends_two_emails(self, mock_send_mail, auth_client, faker):
        response = auth_client.post(
            "/api/users/request-email-change/", {"new_email": faker.email()}
        )
        assert response.status_code == status.HTTP_200_OK
        assert mock_send_mail.call_count == 2

    @patch("apps.users.views.send_mail")
    def test_first_email_goes_to_new_address(
        self, mock_send_mail, auth_client, test_user, faker
    ):
        new_email = faker.email()
        auth_client.post("/api/users/request-email-change/", {"new_email": new_email})
        first_call_recipients = mock_send_mail.call_args_list[0][1]["recipient_list"]
        assert new_email in first_call_recipients

    @patch("apps.users.views.send_mail")
    def test_second_email_goes_to_old_address(
        self, mock_send_mail, auth_client, test_user, faker
    ):
        new_email = faker.email()
        old_email = test_user.email
        auth_client.post("/api/users/request-email-change/", {"new_email": new_email})
        second_call_recipients = mock_send_mail.call_args_list[1][1]["recipient_list"]
        assert old_email in second_call_recipients

    @patch("apps.users.views.send_mail")
    def test_cancel_url_is_in_old_email_body(self, mock_send_mail, auth_client, faker):
        auth_client.post(
            "/api/users/request-email-change/", {"new_email": faker.email()}
        )
        second_call_body = mock_send_mail.call_args_list[1][1]["message"]
        assert "cancel-email-change" in second_call_body

    @patch("apps.users.views.send_mail")
    def test_confirm_url_is_in_new_email_body(self, mock_send_mail, auth_client, faker):
        auth_client.post(
            "/api/users/request-email-change/", {"new_email": faker.email()}
        )
        first_call_body = mock_send_mail.call_args_list[0][1]["message"]
        assert "confirm-email-change" in first_call_body


@pytest.mark.django_db
class TestCancelEmailChange:
    def test_cancel_email_change_success(self, test_user, faker, api_client):
        verification = EmailVerification.objects.create(
            user=test_user, new_email=faker.email()
        )
        api_client.get(
            f"/api/users/cancel-email-change/?token={verification.cancel_token}"
        )
        verification.refresh_from_db()
        assert verification.is_cancelled is True
        assert verification.is_used is False

    def test_cancel_does_not_require_authentication(self, test_user, faker):
        unauthenticated_client = APIClient()
        verification = EmailVerification.objects.create(
            user=test_user, new_email=faker.email()
        )
        url = f"/api/users/cancel-email-change/?token={verification.cancel_token}"
        response = unauthenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_cancel_with_invalid_token(self, api_client):
        url = f"/api/users/cancel-email-change/?token={uuid.uuid4()}"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cancel_without_token(self, api_client):
        url = "/api/users/cancel-email-change/"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cancel_already_cancelled_token(self, test_user, faker, api_client):
        verification = EmailVerification.objects.create(
            user=test_user, new_email=faker.email(), is_cancelled=True
        )
        url = f"/api/users/cancel-email-change/?token={verification.cancel_token}"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cancel_already_used_token(self, test_user, faker, api_client):
        verification = EmailVerification.objects.create(
            user=test_user, new_email=faker.email(), is_used=True
        )
        url = f"/api/users/cancel-email-change/?token={verification.cancel_token}"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cancel_expired_verification(self, test_user, faker, api_client):
        verification = EmailVerification.objects.create(
            user=test_user, new_email=faker.email()
        )
        verification.expires_at = timezone.now() - timedelta(minutes=1)
        verification.save()
        url = f"/api/users/cancel-email-change/?token={verification.cancel_token}"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cancelled_verification_cannot_be_confirmed(
        self, auth_client, test_user, faker
    ):
        verification = EmailVerification.objects.create(
            user=test_user, new_email=faker.email(), is_cancelled=True
        )
        url = "/api/users/confirm-email-change/"
        response = auth_client.post(url, {"code": verification.code})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        test_user.refresh_from_db()
        assert test_user.email != verification.new_email


@pytest.mark.django_db
class TestPreviousVerificationsInvalidated:
    @patch("apps.users.views.send_mail")
    def test_previous_pending_request_is_cancelled(
        self, mock_send_mail, auth_client, test_user, faker
    ):
        old_verification = EmailVerification.objects.create(
            user=test_user, new_email=faker.email()
        )
        assert old_verification.is_cancelled is False

        auth_client.post(
            "/api/users/request-email-change/", {"new_email": faker.email()}
        )

        old_verification.refresh_from_db()
        assert old_verification.is_cancelled is True

    @patch("apps.users.views.send_mail")
    def test_old_code_cannot_confirm_after_new_request(
        self, mock_send_mail, auth_client, test_user, faker
    ):
        old_verification = EmailVerification.objects.create(
            user=test_user, new_email=faker.email()
        )
        old_code = old_verification.code

        auth_client.post(
            "/api/users/request-email-change/", {"new_email": faker.email()}
        )

        url = "/api/users/confirm-email-change/"
        response = auth_client.post(url, {"code": old_code})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("apps.users.views.send_mail")
    def test_only_latest_verification_is_active(
        self, mock_send_mail, auth_client, test_user, faker
    ):
        auth_client.post(
            "/api/users/request-email-change/", {"new_email": faker.email()}
        )
        auth_client.post(
            "/api/users/request-email-change/", {"new_email": faker.email()}
        )
        final_email = faker.email()
        auth_client.post("/api/users/request-email-change/", {"new_email": final_email})

        active = EmailVerification.objects.filter(
            user=test_user, is_cancelled=False, is_used=False
        )
        assert active.count() == 1
        assert active.first().new_email == final_email


@pytest.mark.django_db
class TestConfirmEmailChangeSendsNotification:
    @patch("apps.users.views.send_mail")
    def test_sends_notification_to_old_email_after_confirm(
        self, mock_send_mail, auth_client, test_user, faker
    ):
        old_email = test_user.email
        new_email = faker.email()
        verification = EmailVerification.objects.create(
            user=test_user, new_email=new_email
        )
        auth_client.post(
            "/api/users/confirm-email-change/", {"code": verification.code}
        )

        all_recipients = [
            call[1]["recipient_list"] for call in mock_send_mail.call_args_list
        ]
        assert any(old_email in recipients for recipients in all_recipients)

    @patch("apps.users.views.send_mail")
    def test_email_is_actually_changed_after_confirm(
        self, mock_send_mail, auth_client, test_user, faker
    ):
        new_email = faker.email()
        verification = EmailVerification.objects.create(
            user=test_user, new_email=new_email
        )
        response = auth_client.post(
            "/api/users/confirm-email-change/", {"code": verification.code}
        )
        assert response.status_code == status.HTTP_200_OK
        test_user.refresh_from_db()
        assert test_user.email == new_email


@pytest.mark.django_db
class TestGoogleUserEmailChange:
    @patch("apps.users.views.send_mail")
    def test_google_user_can_request_email_change(
        self, mock_send_mail, api_client, faker
    ):
        user = User.objects.create(email=faker.email(), language="en")
        user.set_unusable_password()
        user.save()
        api_client.force_authenticate(user=user)

        response = api_client.post(
            "/api/users/request-email-change/", {"new_email": faker.email()}
        )
        assert response.status_code == status.HTTP_200_OK
        assert mock_send_mail.call_count == 2

    @patch("apps.users.views.send_mail")
    def test_google_user_can_confirm_email_change(
        self, mock_send_mail, api_client, faker
    ):
        user = User.objects.create(email=faker.email(), language="en")
        user.set_unusable_password()
        user.save()
        api_client.force_authenticate(user=user)

        new_email = faker.email()
        verification = EmailVerification.objects.create(user=user, new_email=new_email)

        response = api_client.post(
            "/api/users/confirm-email-change/", {"code": verification.code}
        )
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.email == new_email
        assert user.has_usable_password() is False


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


@pytest.mark.django_db
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
