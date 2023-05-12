import gzip
from io import BytesIO
from itertools import chain
from json import loads
from datetime import date

from requests import get
from django.core.management.base import BaseCommand
from django.conf import settings

from film_recommender.models import Genre, Movie, Image, Tag
from film_recommender.apps import FilmRecommenderConfig

GenreThroughModel = Movie.genres.through
TagThroughModel = Movie.tags.through


class Command(BaseCommand):
    _movie_tmdb_to_bd_fields = {
        'title': 'title',
        'vote_average': 'rating',
        'overview': 'overview',
        'original_language': 'original_language',
        'runtime': 'duration',
    }

    _batch_size_limit = 500

    _objects_limit = 50

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):

        super().__init__(stdout, stderr, no_color, force_color)

        self.movies_to_create = []
        self.movies_to_update = []

        self.images = {}
        self.movie_genres = {}
        self.movie_tags = {}

    def handle(self, *args, **options):
        bytes_io = self.get_movies_json()
        self.import_movies(bytes_io)

    def get_movies_json(self):
        today = date.today()
        response = get(settings.TMDB_FILES_URL.format(month=today.month, day=today.day, year=today.year))
        bytes_io = BytesIO(response.content)
        return bytes_io

    def import_movies(self, bytes_io):
        movies_in_db = Movie.objects.in_bulk(field_name='tmdb_id')
        movie_ids_with_posters = set(Image.objects.filter(active=True).values_list('movie__tmdb_id', flat=True))
        genres_in_db = set(Genre.objects.values_list('id', flat=True))
        tags_in_db = set(Tag.objects.values_list('id', flat=True))

        file = gzip.GzipFile('movies_json', 'r', fileobj=bytes_io)

        for row in file:
            dict_str = row.decode('UTF-8')
            row = loads(dict_str)

            tmdb_id = row['id']
            tmdb_movie = FilmRecommenderConfig.tmdb.Movies(tmdb_id)
            movie_info = tmdb_movie.info()

            if tmdb_id in movies_in_db:
                got_changes = False
                movie = movies_in_db[tmdb_id]
                for tmdb_field, db_field in self._movie_tmdb_to_bd_fields.items():
                    new_value = movie_info.get(tmdb_field)
                    if getattr(movie, db_field) != new_value:
                        setattr(movie, db_field, new_value)
                        got_changes = True

                if got_changes:
                    self.movies_to_update.append(movie)

            else:
                self.movies_to_create.append(Movie(tmdb_id=tmdb_id,
                                                   title=movie_info['title'],
                                                   rating=movie_info['vote_average'],
                                                   overview=movie_info['overview'],
                                                   original_language=movie_info['original_language'],
                                                   duration=movie_info['runtime'],
                                                   released_at=movie_info['release_date'] or None
                                                   )
                                             )

            if tmdb_id not in movie_ids_with_posters and movie_info['poster_path']:
                self.images[tmdb_id] = settings.TMDB_IMAGE_CDN + movie_info['poster_path']

            self.movie_genres[tmdb_id] = [id_ for genre in movie_info['genres'] if (id_ := genre['id']) in genres_in_db]

            for tag in tmdb_movie.keywords()['keywords']:
                id_ = tag['id']
                if id_ not in tags_in_db:
                    Tag.objects.create(id=id_, name=tag['name'])
                    tags_in_db.add(id_)

                self.movie_tags.setdefault(tmdb_id, []).append(id_)

            self._update_models()

        self._update_models(import_end=True)

    def _update_models(self, import_end=False):
        if len(self.movies_to_create) >= self._objects_limit:
            Movie.objects.bulk_create(self.movies_to_create, batch_size=self._batch_size_limit)
            self.movies_to_create = []

        if len(self.movies_to_update) >= self._objects_limit:
            Movie.objects.bulk_update(self.movies_to_update, batch_size=self._batch_size_limit)
            self.movies_to_update = []

        if any(len(iter) >= self._objects_limit for iter in
               (self.images, self.movie_genres, self.movie_tags)) or import_end:
            tmdb_ids = chain(self.movie_genres.keys(), self.images.keys(), self.movie_tags.keys())
            movie_id_by_tmdb_id = dict(
                Movie.objects.filter(tmdb_id__in=tmdb_ids).values_list('tmdb_id', 'id').iterator()
            )

            self._update_images(movie_id_by_tmdb_id)
            self._update_through(movie_id_by_tmdb_id, GenreThroughModel, self.movie_genres, 'genre_id')
            self._update_through(movie_id_by_tmdb_id, TagThroughModel, self.movie_tags, 'tag_id')

    def _update_images(self, movie_id_by_tmdb_id):
        if self.images:
            Image.objects.bulk_create(
                [Image(movie_id=movie_id_by_tmdb_id[external_id], url=url) for external_id, url in
                 self.images.items()], batch_size=self._batch_size_limit
            )
            self.images = {}

    def _update_through(self, movie_id_by_tmdb_id, ThroughModel, items_dict, field):
        if items_dict:
            for external_id, ids in items_dict.items():
                movie_id = movie_id_by_tmdb_id[external_id]
                new_objects = [ThroughModel(**{field: id_, 'movie_id': movie_id}) for id_ in ids]
                ThroughModel.objects.filter(movie_id=movie_id).delete()

                ThroughModel.objects.bulk_create(new_objects, batch_size=self._batch_size_limit)

            items_dict.clear()
