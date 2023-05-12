from django.apps import AppConfig
from django.conf import settings
import tmdbsimple as tmdb


class FilmRecommenderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'film_recommender'

    tmdb.API_KEY = settings.TMDB_API_KEY
    tmdb = tmdb