# Generated by Django 4.1.4 on 2023-05-18 09:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('film_recommender', '0010_remove_dailyrecommendedfilm_movie_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyRecommendedFilm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('computed_rating', models.FloatField()),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recommended_movies', to='film_recommender.movie', verbose_name='Фильм дня')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Ежедневная рекомендация',
                'verbose_name_plural': 'Ежедневные рекомендации',
            },
        ),
    ]