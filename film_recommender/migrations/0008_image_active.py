# Generated by Django 4.1.4 on 2023-01-06 00:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('film_recommender', '0007_favouritegenre_delete_favouritegenres'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Активна'),
        ),
    ]
