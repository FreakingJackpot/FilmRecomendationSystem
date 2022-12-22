from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.contrib.auth.models import AbstractUser

from django.db import models


# Create your models here.

class CustomUser(AbstractUser):
    about = models.TextField(verbose_name='О себе')

    @classmethod
    def create_user_by_id(cls, user_id):
        username = f'user_{user_id}'
        password = f'PassWord_123_{user_id}'
        email = f'user_{user_id}@yandex.ru'

        email = cls.objects.normalize_email(email)

        username = cls.normalize_username(username)
        user = cls(id=user_id, username=username, email=email)
        user.password = make_password(password)
        user.save()
