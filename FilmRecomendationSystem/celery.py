import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FilmRecomendationSystem.settings')

app = Celery('FilmRecomendationSystem')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

