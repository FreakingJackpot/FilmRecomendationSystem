# Generated by Django 4.1.4 on 2023-06-04 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('film_recommender', '0014_movieproxy'),
    ]

    operations = [
        migrations.AddField(
            model_name='movietranslation',
            name='image_url',
            field=models.TextField(default='/static/images/image_not_available.png'),
        ),
        migrations.AlterField(
            model_name='movie',
            name='released_at',
            field=models.DateField(blank=True, null=True, verbose_name='дата выхода'),
        ),
        migrations.DeleteModel(
            name='Image',
        ),
    ]
