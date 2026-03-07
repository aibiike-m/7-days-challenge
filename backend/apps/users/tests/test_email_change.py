import uuid
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import EmailVerification

User = get_user_model()


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
    def test_verification_code_is_in_new_email_body(
        self, mock_send_mail, auth_client, faker
    ):
        auth_client.post(
            "/api/users/request-email-change/", {"new_email": faker.email()}
        )
        first_call_body = mock_send_mail.call_args_list[0][1]["message"]

        assert "code" in first_call_body.lower() or "код" in first_call_body.lower()
        assert "confirm-email-change" not in first_call_body


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

    @patch("apps.users.views.send_mail")
    def test_cancel_after_email_changed_restores_old_email(
        self, mock_send_mail, test_user, faker, api_client
    ):
        old_email = test_user.email
        new_email = faker.email()

        verification = EmailVerification.objects.create(
            user=test_user, old_email=old_email, new_email=new_email, is_used=True
        )

        test_user.email = new_email
        test_user.save()

        url = f"/api/users/cancel-email-change/?token={verification.cancel_token}"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email_was_restored"] is True

        test_user.refresh_from_db()
        assert test_user.email == old_email

        verification.refresh_from_db()
        assert verification.is_cancelled is True

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
