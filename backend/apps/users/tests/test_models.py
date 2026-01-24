import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestCustomUser:

    def test_create_user_with_email(self, faker):
        email = faker.email()
        password = faker.password()
        user = User.objects.create_user(email=email, password=password)

        assert user.email == email
        assert user.check_password(password)
        assert user.username.startswith("user_")
        assert len(user.username) == 17

    def test_create_user_without_email_raises_error(self):
        with pytest.raises(ValueError):
            User.objects.create_user(email="", password="password123")

    def test_create_superuser(self, faker):
        email = faker.email()
        user = User.objects.create_superuser(email=email, password="adminpass123")

        assert user.is_staff is True
        assert user.is_superuser is True

    def test_username_auto_generation(self, faker):
        user1 = User.objects.create_user(email=faker.email(), password="pass123")
        user2 = User.objects.create_user(email=faker.email(), password="pass123")

        assert user1.username != user2.username
        assert user1.username.startswith("user_")
        assert user2.username.startswith("user_")
