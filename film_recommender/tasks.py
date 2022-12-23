from celery import shared_task
from celery.schedules import crontab

from FilmRecomendationSystem.celery import app
from film_recommender.apps import FilmRecommenderConfig
from film_recommender.services.predictor import Predictor


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(hour=8), import_genres, name='import_genres')
    sender.add_periodic_task(crontab(hour=9), import_movies, name='import_movies')
    sender.add_periodic_task(crontab(minute='*/60'), train_model, name='train_model')
    sender.add_periodic_task(crontab(hour=0, minute=0), predict_daily_recommends, name='predict_daily_recommends')


@shared_task
def import_movies():
    from film_recommender.management.commands.import_movies import Command
    Command().handle()


@shared_task
def import_genres():
    from film_recommender.management.commands.import_genres import Command
    Command().handle()


@shared_task
def train_model():
    from film_recommender.management.commands.train_model import Command
    Command().handle()


@shared_task
def predict_daily_recommends():
    from film_recommender.management.commands.predict_daily_recommends import Command
    Command().handle()


@shared_task
def import_dataset():
    from film_recommender.management.commands.import_dataset import Command
    Command().handle()
