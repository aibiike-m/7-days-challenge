from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    language = models.CharField(
        max_length=5,
        choices=[('ru', 'Русский'), ('en', 'English')],
        default='en'
    )

    def __str__(self):
        return self.username
