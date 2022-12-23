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
        genres = self.import_genres()
        self.import_movies()
        self.import_reviews()

    def import_genres(self):
        Genre.objects.all().delete()
        genres = {}

        with open(os.path.join(APP_DIR, 'datasets', 'ml-100k', 'u.genre')) as csvfile:
            reader = csv.reader(csvfile, delimiter='|')
            for row in reader:
                if row:
                    id_ = row[1]
                    if id_ != '0':
                        name = row[0]
                        genres[name] = Genre(id=id_, name=name)

        Genre.objects.bulk_create(genres.values())

        return genres

    def import_movies(self):
        Movie.objects.all().delete()
        Image.objects.all().delete()

        search = FilmRecommenderConfig.tmbd.Search()

        images = []

        with open(os.path.join(APP_DIR, 'datasets', 'ml-100k', 'u.item'), encoding="ISO-8859-1") as csvfile:
            reader = csv.reader(csvfile, delimiter='|')
            for row in reader:
                title = row[1]
                id_ = row[0]

                year_index = title.rfind('(')
                title = title.replace(title[year_index:], '')

                movies = search.movie(query=title)
                for movie in movies['results']:
                    tmbd_movie = FilmRecommenderConfig.tmbd.Movies(movie['id']).info()
                    movie, _ = Movie.objects.get_or_create(tmbd_id=movie['id'],
                                                           defaults={
                                                               'id': id_,
                                                               'title': title,
                                                               'rating': movie['vote_average'],
                                                               'overview': tmbd_movie['overview'],
                                                               'original_language': tmbd_movie[
                                                                   'original_language'],
                                                               'duration': tmbd_movie['runtime'],
                                                               'released_at': tmbd_movie['release_date'] or None,
                                                           }
                                                           )

                    if tmbd_movie['poster_path']:
                        images.append(Image(movie_id=movie.id, url=settings.TMBD_IMAGE_CDN + tmbd_movie['poster_path']))

                    movie_genres = [id_ for id_, value in enumerate(row[6:], start=1) if int(value)]

                    movie.genres.add(*movie_genres)
                    break

            Image.objects.bulk_create(images, batch_size=500)

    def import_reviews(self):
        data = movielens.load_pandas_df(
            size=MOVIELENS_DATA_SIZE,
            header=[USER_COL, ITEM_COL, RATING_COL],
            genres_col=ITEM_FEAT_COL
        )

        data[ITEM_FEAT_COL] = data[ITEM_FEAT_COL].apply(lambda s: s.split("|"))

        users = set()
        CustomUser.objects.exclude(username='admin').delete()

        movies_ids = set(Movie.objects.values_list('id', flat=True))

        reviews = []
        data = data.reset_index()
        for index, item in data.iterrows():
            if not item[USER_COL] in users:
                CustomUser.create_user_by_id(item[USER_COL])
                users.add(item[USER_COL])
            if item[ITEM_COL] in movies_ids:
                reviews.append(UserReview(user_id=item[USER_COL], movie_id=item[ITEM_COL], rating=item[RATING_COL]))

        UserReview.objects.bulk_create(reviews, batch_size=500)
