from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from film_recommender.prediction_service import Predictor


# Create your models here.
class Movie(TranslatableModel):
    genres = models.ManyToManyField('Genre', verbose_name='Жанры')
    tags = models.ManyToManyField('Tag', verbose_name='Теги')
    tmdb_id = models.IntegerField(db_index=True, unique=True)
    rating = models.FloatField(default=0)
    duration = models.IntegerField(verbose_name='Продолжительность', null=True, blank=True)
    released_at = models.DateField(verbose_name='дата выхода', null=True, blank=True)

    translations = TranslatedFields(
        title=models.TextField(verbose_name='Название'),
        overview=models.TextField(verbose_name='Сюжет', null=True, blank=True),
        image_url=models.TextField(null=True, blank=True)
    )

    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'

    def __str__(self):
        return self.title

    @classmethod
    def get_k_most_rated_without_review(cls, user_id):
        movies = cls.get_most_related_without_review(user_id)[:settings.TOP_K]
        cls.set_predictions_on_movies_for_user(movies, user_id)
        return movies

    @classmethod
    def get_most_related_without_review(cls, user_id):
        movies = cls.objects.prefetch_related('translations').exclude(
            userreview__user_id=user_id).defer('duration', 'released_at').order_by('-rating')
        cls.set_predictions_on_movies_for_user(movies, user_id)
        return movies

    @classmethod
    def get_most_related_without_review_on_genre_with_prediction(cls, user_id, genre_id):
        movies = cls.get_most_rated_without_review_for_genre(user_id, genre_id)
        cls.set_predictions_on_movies_for_user(movies, user_id)
        return movies

    @staticmethod
    def set_predictions_on_movies_for_user(movies, user_id):
        if movies:
            movie_by_id = {movie.id: movie for movie in movies}
            predictions = Predictor.predict(user_id, tuple(movie_by_id.keys()))

            for prediction in predictions:
                movie_by_id[prediction['movie_id']].predicted_rating = prediction['rating']

    @classmethod
    def get_k_most_rated_without_review_for_each_genre(cls, user_id, exclude_movie_ids):
        genres_recommendations = {}
        for genre in Genre.objects.all():
            queryset = cls.get_most_rated_without_review_for_genre(user_id, genre)
            if exclude_movie_ids:
                queryset = queryset.exclude(id__in=exclude_movie_ids)

            movies = queryset[:settings.TOP_K]
            cls.set_predictions_on_movies_for_user(movies, user_id)

            genres_recommendations[genre.name] = movies

        return genres_recommendations

    @classmethod
    def get_most_rated_without_review_for_genre(cls, user_id, genre):
        movies = cls.objects.prefetch_related('translations').filter(genres=genre).exclude(
            userreview__user_id=user_id).order_by('-rating')

        return movies

    @classmethod
    def get_same_genres_recommends(cls, user_id, movie_id, genres):
        movies = cls.objects.exclude(id=movie_id, userreview__user_id=user_id) \
                     .filter(genres__in=genres).defer('duration', 'released_at')[
                 :settings.TOP_K]
        cls.set_predictions_on_movies_for_user(movies, user_id)
        return movies

    @classmethod
    def search(cls, user_id, text):
        movies = cls.objects.filter(translations__title__icontains=text).defer('duration', 'released_at')
        cls.set_predictions_on_movies_for_user(movies, user_id)
        return movies


class Genre(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(verbose_name='Название', max_length=255)
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(verbose_name='Название', max_length=255)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class UserReview(models.Model):
    user = models.ForeignKey('account.CustomUser', verbose_name='Пользователь', on_delete=models.CASCADE)
    movie = models.ForeignKey('Movie', verbose_name='Фильм', on_delete=models.CASCADE)
    rating = models.FloatField()

    class Meta:
        verbose_name = 'Отзыв пользователя'
        verbose_name_plural = 'Отзывы пользователя'

    def __str__(self):
        return f'{self.user.username}_{self.movie.title}_{self.rating}'

    @classmethod
    def get_user_reviews(cls, user_id):
        return cls.objects.filter(user_id=user_id).prefetch_related('movie__translations')

    @classmethod
    def create_user_reviews(cls, user_id, data):
        movie_id_by_tmdb_id = dict(
            cls.objects.filter(movie__tmdb_id__in=[i['tmdb_id'] for i in data]).values_list('movie__tmdb_id',
                                                                                            'movie_id')
        )
        objects = [
            cls(movie_id=movie_id_by_tmdb_id.get(item['tmdb_id']), user_id=user_id, rating=item['rating']) for
            item in data
        ]

        cls.objects.bulk_create(objects)

    @classmethod
    def update_user_reviews(cls, user_id, data):
        reviews = cls.objects.filter(user_id=user_id, movie__tmdb_id__in=[i['tmdb_id'] for i in data]).select_related(
            'movie').only('rating', 'movie__tmdb_id')
        review_by_tmdb_id = {review.movie.tmdb_id: review for review in reviews}

        for item in data:
            review = review_by_tmdb_id.get(item['tmdb_id'])
            review.rating = item['rating']

        cls.objects.bulk_update(review_by_tmdb_id.values(), fields=['rating', ])


class DailyRecommendedFilm(models.Model):
    user = models.ForeignKey('account.CustomUser', verbose_name='Пользователь', on_delete=models.CASCADE)
    movie = models.ForeignKey('Movie', verbose_name='Фильм дня', related_name='recommended_movies',
                              on_delete=models.CASCADE)
    predicted_rating = models.FloatField()

    class Meta:
        verbose_name = 'Ежедневная рекомендация'
        verbose_name_plural = 'Ежедневные рекомендации'

    def __str__(self):
        return f'{self.user.username}_{self.movie.title}_{self.predicted_rating}'

    @classmethod
    def get_user_recommendations(cls, user_id):
        return cls.objects.filter(user_id=user_id).prefetch_related('movie__translations').prefetch_related(
            'movies__movie__genres')


class FavouriteGenre(models.Model):
    user = models.ForeignKey('account.CustomUser', verbose_name='Пользователь', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', verbose_name='Жанры', on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'genre']
        verbose_name_plural = _('Favourite genres')
        verbose_name = _('Favourite genre')


