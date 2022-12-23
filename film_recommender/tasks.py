from celery import shared_task

from FilmRecomendationSystem.celery import app
from celery.schedules import crontab


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(hour=8), import_genres, name='import_genres')
    sender.add_periodic_task(crontab(hour=9), import_movies, name='import_movies')


@shared_task
def import_movies():
    from film_recommender.management.commands.import_movies import Command
    Command().handle()


@shared_task
def import_genres():
    from film_recommender.management.commands.import_genres import Command
    Command().handle()


@shared_task
def import_dataset():
    from film_recommender.management.commands.import_dataset import Command
    Command().handle()
