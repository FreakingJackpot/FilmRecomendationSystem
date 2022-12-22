from django.apps import AppConfig
from django.conf import settings
import tmdbsimple as tmbd


class FilmRecommenderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'film_recommender'

    tmbd.API_KEY = settings.TMBD_API_KEY
    tmbd = tmbd
