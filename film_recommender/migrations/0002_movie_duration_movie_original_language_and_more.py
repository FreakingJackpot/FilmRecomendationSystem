# Generated by Django 4.1.4 on 2022-12-22 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('film_recommender', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='duration',
            field=models.IntegerField(blank=True, null=True, verbose_name='Продолжительность'),
        ),
        migrations.AddField(
            model_name='movie',
            name='original_language',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Язык оригинала'),
        ),
        migrations.AddField(
            model_name='movie',
            name='overview',
            field=models.TextField(blank=True, null=True, verbose_name='Сюжет'),
        ),
        migrations.AddField(
            model_name='movie',
            name='released_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='дата выхода'),
        ),
        migrations.AlterField(
            model_name='movie',
            name='rating',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='movie',
            name='title',
            field=models.TextField(verbose_name='Название'),
        ),
    ]
