import csv
import os
from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings
import pandas as pd

from film_recommender.models import Genre, Movie, UserReview, Image, Tag
from film_recommender.apps import FilmRecommenderConfig
from portal.models import CustomUser

APP_DIR = Path(__file__).resolve().parent.parent.parent

USER_COLUMN = 'userId'
ITEM_COLUMN = 'movieId'
RATING_COLUMN = 'rating'


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.import_genres()
        self.import_tags()
        self.import_movies_and_ratings()

    def import_genres(self):
        Genre.objects.all().delete()
        genres = []

        with open(os.path.join(APP_DIR, 'datasets', 'genres.csv')) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            next(reader)
            for row in reader:
                if row:
                    id_ = int(row[0]) + 1
                    name = row[1]
                    genres.append(Genre(id=id_, name=name))

        Genre.objects.bulk_create(genres)

    def import_tags(self):
        Tag.objects.all().delete()
        tags = []

        with open(os.path.join(APP_DIR, 'datasets', 'tags.csv')) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for idx, row in enumerate(reader):
                if row and idx:
                    name = row[1]
                    tags.append(Tag(id=idx, name=name))

        Tag.objects.bulk_create(tags)

    def import_movies_and_ratings(self):
        dataset = pd.read_pickle(os.path.join(APP_DIR, 'datasets', 'dataset.pkl'))
        self._import_movies(dataset)
        self._import_reviews(dataset)

    def _import_movies(self, dataset):
        Movie.objects.all().delete()
        Image.objects.all().delete()

        all_genres = {genre.name: genre.id for genre in Genre.objects.all().iterator()}
        all_tags = {tag.name: tag.id for tag in Tag.objects.all().iterator()}

        images = []

        movies_info = dataset.drop_duplicates(subset='movieId', keep="last")
        for idx, row in movies_info.iterrows():
            id_ = row['movieId']
            tmdb_id = int(row['tmdbId'])
            try:
                movie_info = FilmRecommenderConfig.tmdb.Movies(int(row['tmdbId'])).info()
                movie, _ = Movie.objects.get_or_create(tmdb_id=tmdb_id,
                                                       defaults={
                                                           'id': id_,
                                                           'title': movie_info['title'],
                                                           'rating': movie_info['vote_average'],
                                                           'overview': movie_info['overview'],
                                                           'original_language': movie_info['original_language'],
                                                           'duration': movie_info['runtime'],
                                                           'released_at': movie_info['release_date'] or None,
                                                       }
                                                       )

                if movie_info['poster_path']:
                    images.append(Image(movie_id=movie.id, url=settings.TMDB_IMAGE_CDN + movie_info['poster_path']))

                movie_genres = [all_genres[genre_name] for genre_name in row['genres'] if genre_name in all_genres]
                movie.genres.add(*movie_genres)

                movie_tags = [all_tags[tag_name] for tag_name in row['tags'] if tag_name in all_tags]
                movie.tags.add(*movie_tags)

            except:
                pass

        Image.objects.bulk_create(images, batch_size=500)

    def _import_reviews(self, dataset):

        users = set()
        CustomUser.objects.exclude(username='admin').delete()

        movies_ids = set(Movie.objects.values_list('id', flat=True))

        reviews = []
        for idx, row in dataset.iterrows():
            if not row[USER_COLUMN] in users:
                CustomUser.create_user_by_id(row[USER_COLUMN])
                users.add(row[USER_COLUMN])

            if row[ITEM_COLUMN] in movies_ids:
                reviews.append(
                    UserReview(user_id=row[USER_COLUMN], movie_id=row[ITEM_COLUMN], rating=row[RATING_COLUMN]))

        UserReview.objects.bulk_create(reviews, batch_size=500)
