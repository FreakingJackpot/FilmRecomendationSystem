import gzip
from collections import defaultdict
from io import BytesIO
from itertools import chain
from json import loads
from datetime import date

from requests import get
from django.core.management.base import BaseCommand
from django.conf import settings

from film_recommender.models import Genre, Movie, Tag
from film_recommender.apps import FilmRecommenderConfig

MovieTranslationModel = Movie.translations.fields.model
GenreThroughModel = Movie.genres.through
TagThroughModel = Movie.tags.through


class Command(BaseCommand):
    _tmdb_to_bd_fields = {
        'vote_average': 'rating',
        'runtime': 'duration',
    }

    _tmdb_to_db_translation_fields = {
        'title': 'title',
        'overview': 'overview',
        'poster_path': 'image_url'
    }

    _batch_size_limit = 500

    _objects_limit = 500

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):

        super().__init__(stdout, stderr, no_color, force_color)

        self.movies_to_create = []
        self.movies_to_update = []
        self.translations_to_create = defaultdict(list)
        self.translations_to_update = []
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
            languages_info = (('en-us', movie_info), ('ru', movie_info_ru))

            if tmdb_id in movies_in_db:
                movie = movies_in_db[tmdb_id]
                got_changes = self._update_movie_model(movie, movie_info, self._tmdb_to_bd_fields)
                if got_changes:
                    self.movies_to_update.append(movie)

                self._update_movie_translation_model(movie.id, languages_info)
            else:
                movie = Movie(tmdb_id=tmdb_id,
                              rating=movie_info['vote_average'] / 2,
                              overview=movie_info['overview'],
                              duration=movie_info['runtime'],
                              released_at=movie_info.get('release_date'),
                              )
                self.movies_to_create.append(movie)

                self._create_movie_translations(tmdb_id, languages_info)

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
    def _update_movie_model(movie, movie_info, fields_map):
        got_changes = False
        for tmdb_field, db_field in fields_map.items():
            new_value = movie_info.get(tmdb_field)

            if tmdb_field == 'poster_path':
                new_value = settings.TMDB_IMAGE_CDN + new_value if new_value else None

            if getattr(movie, db_field) != new_value:
                setattr(movie, db_field, new_value)
                got_changes = True

        return got_changes

    def _update_movie_translation_model(self, movie_id, data):
        for language_code, movie_info_ in data:
            if movie_info_:
                obj = MovieTranslationModel.objects.filter(language_code=language_code,
                                                           master_id=movie_id).first()
                if obj:
                    got_changes = self._update_movie_model(obj, movie_info_, self._tmdb_to_db_translation_fields)
                    if got_changes:
                        self.translations_to_update.append(obj)

    def _create_movie_translations(self, tmdb_id, languages_info):
        for language_code, movie_info_ in languages_info:
            if poster_path := movie_info_.get('poster_path'):
                image_url = settings.TMDB_IMAGE_CDN + poster_path
            else:
                image_url = None

            self.translations_to_create[tmdb_id].append(
                MovieTranslationModel(language_code=language_code,
                                      title=movie_info_.get('title'),
                                      overview=movie_info_.get('overview'),
                                      image_url=image_url,
                                      )
            )

    def _update_models(self, import_end=False):
        create_iters = (self.movie_genres, self.movie_tags, self.translations_to_create, self.movies_to_create)
        if self._is_need_update(create_iters, import_end):
            tmdb_ids = chain(self.movie_genres.keys(), self.movie_tags.keys(), self.translations_to_create.keys())

            Movie.objects.bulk_create(self.movies_to_create, batch_size=self._batch_size_limit)

            movie_id_by_tmdb_id = dict(
                Movie.objects.filter(tmdb_id__in=tmdb_ids).values_list('tmdb_id', 'id').iterator()
            )

            self._update_translations(movie_id_by_tmdb_id, self.translations_to_create)
            self._update_through(movie_id_by_tmdb_id, GenreThroughModel, self.movie_genres, 'genre_id')
            self._update_through(movie_id_by_tmdb_id, TagThroughModel, self.movie_tags, 'tag_id')

        if self._is_need_update((self.movies_to_update, self.translations_to_update), import_end):
            Movie.objects.bulk_update(self.movies_to_update, fields=self._tmdb_to_bd_fields.values(),
                                      batch_size=self._batch_size_limit)
            MovieTranslationModel.objects.bulk_update(self.translations_to_update,
                                                      fields=self._tmdb_to_db_translation_fields.values(),
                                                      batch_size=self._batch_size_limit)

    def _is_need_update(self, list_of_iters, import_end):
        return any(len(iter) >= self._objects_limit for iter in list_of_iters) or import_end

    def _update_through(self, movie_id_by_tmdb_id, ThroughModel, items_dict, field):
        if items_dict:
            for external_id, ids in items_dict.items():
                movie_id = movie_id_by_tmdb_id[external_id]
                new_objects = [ThroughModel(**{field: id_, 'movie_id': movie_id}) for id_ in ids]
                ThroughModel.objects.filter(movie_id=movie_id).delete()

                ThroughModel.objects.bulk_create(new_objects, batch_size=self._batch_size_limit)

            items_dict.clear()

    def _update_translations(self, movie_id_by_tmdb_id, items_dict):
        if items_dict:
            for external_id, objects in items_dict.items():
                movie_id = movie_id_by_tmdb_id[external_id]
                for obj in objects:
                    obj.master_id = movie_id

                MovieTranslationModel.objects.bulk_create(chain(*items_dict.values()),
                                                          batch_size=self._batch_size_limit)

            items_dict.clear()
