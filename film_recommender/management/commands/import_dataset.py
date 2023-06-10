import csv
import os
from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings
import pandas as pd

from film_recommender.models import Genre, Movie, UserReview, Tag
from film_recommender.apps import FilmRecommenderConfig
from account.models import CustomUser, Occupation

APP_DIR = Path(__file__).resolve().parent.parent.parent

USER_COLUMN = 'userId'
ITEM_COLUMN = 'movieId'
RATING_COLUMN = 'rating'


class Command(BaseCommand):
    _movie_tmdb_to_bd_fields = {
        'title': 'title',
        'overview': 'overview',
    }

    def handle(self, *args, **options):
        self.import_genres()
        self.import_tags()
        self.import_movies_and_ratings()

    def import_genres(self):
        Genre.objects.all().delete()

        with open(os.path.join(APP_DIR, 'datasets', 'genres.csv')) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            next(reader)
            for row in reader:
                if row:
                    id_ = int(row[0]) + 1
                    name = row[1]
                    Genre.objects.create(id=id_, name=name)

    def import_tags(self):
        Tag.objects.all().delete()

        with open(os.path.join(APP_DIR, 'datasets', 'tags.csv')) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for idx, row in enumerate(reader):
                if row and idx:
                    name = row[1]
                    Tag.objects.create(id=idx, name=name)

    def import_occupations(self, dataset):
        Occupation.objects.all().delete()
        for idx, row in enumerate(list(dataset.occupation.unique()), 1):
            if row and idx:
                name = row
                Occupation.objects.create(id=idx, name=name)

    def import_movies_and_ratings(self):
        dataset = pd.read_pickle(os.path.join(APP_DIR, 'datasets', 'dataset.pkl'))
        self.import_occupations(dataset)
        self._import_movies(dataset)
        self._import_reviews(dataset)

    def _import_movies(self, dataset):
        Movie.objects.all().delete()

        all_genres = {genre.name: genre.id for genre in Genre.objects.all().iterator()}
        all_tags = {tag.name: tag.id for tag in Tag.objects.all().iterator()}

        movies_info = dataset.drop_duplicates(subset='movieId', keep="last")
        for idx, row in movies_info.iterrows():
            id_ = row['movieId']
            tmdb_id = int(row['tmdbId'])
            try:
                movie_info = FilmRecommenderConfig.tmdb.Movies(int(row['tmdbId'])).info()
                movie_info_ru = FilmRecommenderConfig.tmdb.Movies(int(row['tmdbId'])).info(language='ru')
                movie = Movie(tmdb_id=tmdb_id,
                              id=id_,
                              title=movie_info['title'],
                              rating=movie_info['vote_average'] / 2,
                              overview=movie_info['overview'],
                              duration=movie_info['runtime'],
                              released_at=movie_info['release_date'] or None,
                              image_url=settings.TMDB_IMAGE_CDN + movie_info['poster_path'],
                              )
                movie.set_current_language('ru')
                for tmdb_field, db_field in self._movie_tmdb_to_bd_fields.items():
                    new_value = movie_info_ru.get(tmdb_field)
                    setattr(movie, db_field, new_value)

                movie.image_url = settings.TMDB_IMAGE_CDN + movie_info_ru['poster_path']
                movie.save()

                movie_genres = [all_genres[genre_name] for genre_name in row['genres'] if genre_name in all_genres]
                movie.genres.add(*movie_genres)

                movie_tags = [all_tags[tag_name] for tag_name in row['tags'] if tag_name in all_tags]
                movie.tags.add(*movie_tags)

            except Exception as e:
                print(e)

    def _import_reviews(self, dataset):

        users = set()
        CustomUser.objects.exclude(username='admin').delete()

        occupation_id_by_name = {occupation.name: occupation.id for occupation in Occupation.objects.all()}

        movies_ids = set(Movie.objects.values_list('id', flat=True))

        reviews = []
        for idx, row in dataset.iterrows():
            if not row[USER_COLUMN] in users:
                CustomUser.create_test_user_by_id(row[USER_COLUMN],
                                                  row['age'],
                                                  row['gender'],
                                                  occupation_id_by_name[row['occupation']],
                                                  row['country'])
                users.add(row[USER_COLUMN])

            if row[ITEM_COLUMN] in movies_ids:
                reviews.append(
                    UserReview(user_id=row[USER_COLUMN], movie_id=row[ITEM_COLUMN], rating=row[RATING_COLUMN]))

        UserReview.objects.bulk_create(reviews, batch_size=500)
