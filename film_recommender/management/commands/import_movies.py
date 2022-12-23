import gzip
from io import BytesIO
from json import loads
from datetime import date

from requests import get
from django.core.management.base import BaseCommand
from django.conf import settings

from film_recommender.models import Genre, Movie, Image
from film_recommender.apps import FilmRecommenderConfig


class Command(BaseCommand):
    _movie_tmbd_to_bd_fields = {
        'title': 'title',
        'vote_average': 'rating',
        'overview': 'overview',
        'original_language': 'original_language',
        'runtime': 'duration',
    }

    objects_limit = 5000

    def handle(self, *args, **options):
        bytes_io = self.get_movies_json()
        self.import_movies(bytes_io)

    def get_movies_json(self):
        today = date.today()
        response = get(settings.TMBD_FILES_URL.format(month=today.month, day=today.day, year=today.year))
        bytes_io = BytesIO(response.content)
        return bytes_io

    def import_movies(self, bytes_io):
        movies_in_db = Movie.objects.in_bulk(field_name='tmbd_id')
        genres_in_db = set(Genre.objects.values_list('id', flat=True))

        file = gzip.GzipFile('movies_json', 'r', fileobj=bytes_io)

        images = []
        movies_to_update = []
        for row in file:
            dict_str = row.decode('UTF-8')
            row = loads(dict_str)
            tmbd_id = row['id']
            tmbd_movie = FilmRecommenderConfig.tmbd.Movies(tmbd_id).info()
            if tmbd_id in movies_in_db:
                got_changes = False
                movie = movies_in_db[tmbd_id]
                for tmbd_field, db_field in self._movie_tmbd_to_bd_fields:
                    new_value = tmbd_movie[tmbd_field]
                    if getattr(movie, db_field) != new_value:
                        setattr(movie, db_field, new_value)
                        got_changes = True

                if movie.released_at != tmbd_movie['release_date']:
                    movie.released_at = tmbd_movie['release_date'] or None
                    got_changes = True

                if got_changes:
                    movies_to_update.append(movie)

            else:
                movie = Movie.objects.create(tmpb_id=tmbd_movie['id'],
                                             title=tmbd_movie['title'],
                                             rating=tmbd_movie['vote_average'],
                                             overview=tmbd_movie['overview'],
                                             original_language=tmbd_movie['original_language'],
                                             duration=tmbd_movie['runtime'],
                                             released_at=tmbd_movie['release_date'] or None
                                             )

            if tmbd_movie['poster_path']:
                images.append(Image(movie_id=movie.id, url=settings.TMBD_IMAGE_CDN + tmbd_movie['poster_path']))

            movie_genres = [id_ for genre in tmbd_movie['genres'] if (id_ := genre['id']) in genres_in_db]

            movie.genres.set(*movie_genres)

            if len(images) >= self.objects_limit:
                Image.objects.bulk_create(images, batch_size=500)
                images = []

            if len(movies_to_update) >= self.objects_limit:
                Movie.objects.bulk_update(movies_to_update, batch_size=500)
                movies_to_update = []

        if images:
            Image.objects.bulk_create(images, batch_size=500)

        if movies_to_update:
            Movie.objects.bulk_update(movies_to_update, batch_size=500)
