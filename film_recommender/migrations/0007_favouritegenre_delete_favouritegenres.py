# Generated by Django 4.1.4 on 2023-01-06 00:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('film_recommender', '0006_alter_dailyrecommendedfilm_movie_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FavouriteGenre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='film_recommender.genre', verbose_name='Жанры')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'unique_together': {('user', 'genre')},
            },
        ),
        migrations.DeleteModel(
            name='FavouriteGenres',
        ),
    ]
