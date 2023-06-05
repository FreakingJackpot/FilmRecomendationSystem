from pathlib import Path

from django.core.management.base import BaseCommand

from film_recommender.models import Genre
from film_recommender.apps import FilmRecommenderConfig

MOVIELENS_DATA_SIZE = '100k'

APP_DIR = Path(__file__).resolve().parent.parent.parent


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.import_genres()

    def import_genres(self):
        existing_genres = {genre.id: genre for genre in Genre.objects.all()}

        genres_api = FilmRecommenderConfig.tmdb.Genres()
        all_genres = genres_api.movie_list()
        all_genres_ru = genres_api.movie_list(language='ru')

        for genre, genre_rus in zip(all_genres['genres'], all_genres_ru['genres']):
            genre_obj = existing_genres.get(genre['id'])
            if genre_obj:
                genre_obj = Genre.objects.create(id=genre['id'], name=genre['name'])

            genre_obj.set_current_language('ru')
            genre.name = genre_rus['name']
            genre.save()
