# Generated by Django 4.1.4 on 2023-06-05 12:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('film_recommender', '0016_alter_movietranslation_image_url'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MovieProxy',
        ),
    ]
