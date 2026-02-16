import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db, faker):
    return User.objects.create_user(
        email=faker.email(), password="testpass123", language="en"
    )


@pytest.fixture
def auth_client(api_client, test_user):
    api_client.force_authenticate(user=test_user)
    api_client.user = test_user
    return api_client


@pytest.fixture
def oauth_user(db, faker):
    user = User.objects.create(email=faker.email(), language="en")
    user.set_unusable_password()
    user.save()
    return user


@pytest.fixture
def oauth_client(api_client, oauth_user):
    api_client.force_authenticate(user=oauth_user)
    api_client.user = oauth_user
    return api_client
