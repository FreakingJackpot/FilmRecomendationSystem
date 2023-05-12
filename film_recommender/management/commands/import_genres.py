import csv
import os
from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings
from recommenders.utils.constants import (
    DEFAULT_USER_COL as USER_COL,
    DEFAULT_ITEM_COL as ITEM_COL,
    DEFAULT_RATING_COL as RATING_COL,
    DEFAULT_GENRE_COL as ITEM_FEAT_COL,
)
from recommenders.datasets import movielens

from film_recommender.models import Genre, Movie, UserReview, Image
from film_recommender.apps import FilmRecommenderConfig
from portal.models import CustomUser

MOVIELENS_DATA_SIZE = '100k'

APP_DIR = Path(__file__).resolve().parent.parent.parent


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.import_genres()


    def import_genres(self):
        existing_genres = set(Genre.objects.values_list('id', flat=True))

        genres_api = FilmRecommenderConfig.tmdb.Genres()
        all_genres = genres_api.movie_list()

        need_to_create = []
        for genre in all_genres['genres']:
            if genre['id'] not in existing_genres:
                need_to_create.append(Genre(id=genre['id'], name=genre['name']))

        Genre.objects.bulk_create(need_to_create, batch_size=500)
