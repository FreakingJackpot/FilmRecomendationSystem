# Generated by Django 4.1.4 on 2022-12-22 08:03

from django.conf import settings
import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion
from django.contrib.postgres.operations import BtreeGinExtension


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        BtreeGinExtension(),
        migrations.CreateModel(
            name='DailyRecommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Ежедневная рекомендация',
                'verbose_name_plural': 'Ежедневные рекомендации',
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Жанр',
                'verbose_name_plural': 'Жанры',
            },
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(db_index=True, verbose_name='Название')),
                ('tmpb_id', models.IntegerField(db_index=True)),
                ('rating', models.FloatField()),
                ('genres', models.ManyToManyField(to='film_recommender.genre', verbose_name='Жанры')),
            ],
            options={
                'verbose_name': 'Фильм',
                'verbose_name_plural': 'Фильмы',
            },
        ),
        migrations.CreateModel(
            name='UserReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.FloatField()),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='film_recommender.movie',
                                            verbose_name='Фильм')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL,
                                           verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Отзыв пользователя',
                'verbose_name_plural': 'Отзывы пользователя',
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.TextField()),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images',
                                            to='film_recommender.movie', verbose_name='Фильм')),
            ],
            options={
                'verbose_name': 'Картинка',
                'verbose_name_plural': 'Картинки',
            },
        ),
        migrations.CreateModel(
            name='FavouriteGenres',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genres', models.ManyToManyField(to='film_recommender.genre', verbose_name='Жанры')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL,
                                           verbose_name='Пользователь')),
            ],
        ),
        migrations.CreateModel(
            name='DailyRecommendedFilm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('computed_rating', models.FloatField()),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='film_recommender.movie',
                                            verbose_name='Фильм дня')),
                ('recommendation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                                     to='film_recommender.dailyrecommendation',
                                                     verbose_name='рекомендация')),
            ],
            options={
                'verbose_name': 'Ежедневная рекомендация',
                'verbose_name_plural': 'Ежедневные рекомендации',
            },
        ),
        migrations.AddField(
            model_name='dailyrecommendation',
            name='movies',
            field=models.ManyToManyField(to='film_recommender.movie', verbose_name='Фильмы дня'),
        ),
        migrations.AddField(
            model_name='dailyrecommendation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL,
                                    verbose_name='Пользователь'),
        ),
        migrations.AddIndex(
            model_name='movie',
            index=django.contrib.postgres.indexes.GinIndex(fields=['title'], name='movie_title_gin'),
        ),
    ]
