import gzip
from io import BytesIO
from itertools import chain
from json import loads
from datetime import date

from requests import get
from django.core.management.base import BaseCommand
from django.conf import settings

from film_recommender.models import Genre, Movie, Tag, Movie
from film_recommender.apps import FilmRecommenderConfig

GenreThroughModel = Movie.genres.through
TagThroughModel = Movie.tags.through


class Command(BaseCommand):
    _movie_tmdb_to_bd_fields = {
        'title': 'title',
        'vote_average': 'rating',
        'overview': 'overview',
        'runtime': 'duration',
        'poster_path': 'image_url'
    }

    _movie_tmdb_to_bd_ru_fields = {
        'title': 'title',
        'overview': 'overview',
        'poster_path': 'image_url'
    }

    _batch_size_limit = 500

    _objects_limit = 500

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):

        super().__init__(stdout, stderr, no_color, force_color)

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
        genres_in_db = set(Genre.objects.values_list('id', flat=True))
        tags_in_db = set(Tag.objects.values_list('id', flat=True))

        file = gzip.GzipFile('movies_json', 'r', fileobj=bytes_io)

        for row in file:
            dict_str = row.decode('UTF-8')
            row = loads(dict_str)

            tmdb_id = row['id']
            tmdb_movie = FilmRecommenderConfig.tmdb.Movies(tmdb_id)
            movie_info = tmdb_movie.info()
            movie_info_ru = tmdb_movie.info(language='ru')

            if tmdb_id in movies_in_db:
                movie = movies_in_db[tmdb_id]
                got_changes = self._update_movie(movie, movie_info, self._movie_tmdb_to_bd_fields)
            else:
                movie = Movie(tmdb_id=tmdb_id,
                              title=movie_info['title'],
                              rating=movie_info['vote_average'] / 2,
                              overview=movie_info['overview'],
                              duration=movie_info['runtime'],
                              released_at=movie_info['release_date'] or None,
                              image_url=settings.TMDB_IMAGE_CDN + movie_info['poster_path'] if movie_info[
                                  'poster_path'] else None,
                              )
                got_changes = True

            movie.set_current_language('ru')
            ru_got_changes = self._update_movie(movie, movie_info_ru, self._movie_tmdb_to_bd_ru_fields)

            if got_changes or ru_got_changes:
                movie.save()

            self.movie_genres[tmdb_id] = [id_ for genre in movie_info['genres'] if (id_ := genre['id']) in genres_in_db]

            for tag in tmdb_movie.keywords()['keywords']:
                id_ = tag['id']
                if id_ not in tags_in_db:
                    Tag.objects.create(id=id_, name=tag['name'])
                    tags_in_db.add(id_)

                self.movie_tags.setdefault(tmdb_id, []).append(id_)

            self._update_models()

        self._update_models(import_end=True)

    @staticmethod
    def _update_movie(movie, movie_info, fields_map):
        got_changes = False
        for tmdb_field, db_field in fields_map.items():
            new_value = movie_info.get(tmdb_field)

            if tmdb_field == 'poster_path':
                new_value = settings.TMDB_IMAGE_CDN + new_value if new_value else None

            if getattr(movie, db_field) != new_value:
                setattr(movie, db_field, new_value)
                got_changes = True

        return got_changes

    def _update_models(self, import_end=False):
        if any(len(iter) >= self._objects_limit for iter in
               (self.movie_genres, self.movie_tags)) or import_end:
            tmdb_ids = chain(self.movie_genres.keys(), self.movie_tags.keys())
            movie_id_by_tmdb_id = dict(
                Movie.objects.filter(tmdb_id__in=tmdb_ids).values_list('tmdb_id', 'id').iterator()
            )

            self._update_through(movie_id_by_tmdb_id, GenreThroughModel, self.movie_genres, 'genre_id')
            self._update_through(movie_id_by_tmdb_id, TagThroughModel, self.movie_tags, 'tag_id')

    def _update_through(self, movie_id_by_tmdb_id, ThroughModel, items_dict, field):
        if items_dict:
            for external_id, ids in items_dict.items():
                movie_id = movie_id_by_tmdb_id[external_id]
                new_objects = [ThroughModel(**{field: id_, 'movie_id': movie_id}) for id_ in ids]
                ThroughModel.objects.filter(movie_id=movie_id).delete()

                ThroughModel.objects.bulk_create(new_objects, batch_size=self._batch_size_limit)

            items_dict.clear()
