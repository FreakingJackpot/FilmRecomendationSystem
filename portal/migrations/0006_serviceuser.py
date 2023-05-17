# Generated by Django 4.1.4 on 2023-05-16 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0005_remove_customuser_master_token'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.TextField()),
                ('password', models.TextField()),
                ('approved', models.BooleanField(default=False)),
            ],
        ),
    ]