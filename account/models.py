from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models
from parler.models import  TranslatedFields, TranslatableModel
from django_countries.fields import CountryField

GENDERS = [
    ('M', _('Male')),
    ('F', _('Female')),
]

AGES = [
    ('0-17', '0-17'),
    ('18-24', '18-24'),
    ('25-34', '25-34'),
    ('35-44', '35-44'),
    ('45-49', '45-49'),
    ('50-55', '50-55'),
    ('56+', '56+'),
]


# Create your models here.

class Occupation(TranslatableModel):
    translations = TranslatedFields(
        name=models.TextField(verbose_name=_('Name')),
    )

    class Meta:
        verbose_name = _('Occupation')
        verbose_name_plural = _('Occupations')

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    favourite_genres = models.ManyToManyField(through='film_recommender.FavouriteGenre', to='film_recommender.Genre')
    gender = models.CharField(max_length=1, verbose_name=_('Gender'), choices=GENDERS, null=True)
    country = CountryField(verbose_name=_('Country'), null=True)
    occupation = models.ForeignKey(Occupation, verbose_name=_('Occupation'), on_delete=models.CASCADE, null=True)
    age = models.CharField(max_length=15, verbose_name=_('Age'), choices=AGES, default=AGES[1][0])

    @classmethod
    def create_test_user_by_id(cls, user_id, age, gender, occupation, country):
        username = f'user_{user_id}'
        password = f'PassWord_123_{user_id}'
        email = f'user_{user_id}@yandex.ru'

        email = cls.objects.normalize_email(email)
        username = cls.normalize_username(username)

        country = None if country == 'unknown country' else country
        user = cls(id=user_id, username=username, email=email, age=age, gender=gender, occupation_id=occupation,
                   country=country)
        user.password = make_password(password)
        user.save()


class ServiceUser(models.Model):
    username = models.TextField()
    password = models.TextField()
    approved = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Service user')
        verbose_name_plural = _('Service users')
