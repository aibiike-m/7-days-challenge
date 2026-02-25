import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

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
