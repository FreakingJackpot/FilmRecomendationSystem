from django.conf import settings
from django.apps import apps
from django.contrib.postgres.indexes import GinIndex
from django.db import models


# Create your models here.
class Movie(models.Model):
    title = models.TextField(verbose_name='Название')
    genres = models.ManyToManyField('Genre', verbose_name='Жанры')
    tmbd_id = models.IntegerField(db_index=True, unique=True)
    rating = models.FloatField(default=0)
    overview = models.TextField(verbose_name='Сюжет', null=True, blank=True)
    duration = models.IntegerField(verbose_name='Продолжительность', null=True, blank=True)
    original_language = models.CharField(max_length=255, verbose_name='Язык оригинала', null=True, blank=True)
    released_at = models.DateTimeField(verbose_name='дата выхода', null=True, blank=True)

    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'
        indexes = [GinIndex(name='movie_title_gin', fields=['title']), ]

    def __str__(self):
        return self.title

    @classmethod
    def get_k_most_rated_without_review(cls, user_id):
        movies = cls.get_most_related_without_review(user_id)[:settings.TOP_K]
        cls.set_predictions_on_movies_for_user(movies, user_id)
        return movies

    @classmethod
    def get_most_related_without_review(cls, user_id):
        movies = cls.objects.prefetch_related('images', 'genres').exclude(userreview__user_id=user_id).order_by(
            '-rating')
        cls.set_predictions_on_movies_for_user(movies, user_id)
        return movies

    @classmethod
    def get_most_related_without_review_on_genre_with_prediction(cls, user_id, genre_id):
        movies = cls.get_most_rated_without_review_for_genre(user_id, genre_id)
        cls.set_predictions_on_movies_for_user(movies, user_id)
        return movies

    @staticmethod
    def set_predictions_on_movies_for_user(movies, user_id):
        predictor = apps.get_app_config('film_recommender').predictor
        predictions = predictor.predict(movies, user_id)
        for movie, prediction in zip(movies, predictions):
            movie.predicted_rating = prediction

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
        movies = cls.objects.prefetch_related('images', 'genres').filter(genres=genre).exclude(
            userreview__user_id=user_id).order_by('-rating')

        return movies

    @classmethod
    def get_same_genres_recommends(cls, user_id, movie_id, genres):
        movies = cls.objects.exclude(id=movie_id, userreview__user_id=user_id).filter(genres__in=genres)[
                 :settings.TOP_K]
        cls.set_predictions_on_movies_for_user(movies, user_id)
        return movies


class Image(models.Model):
    movie = models.ForeignKey('Movie', related_name='images', verbose_name='Фильм', on_delete=models.CASCADE)
    url = models.TextField()

    class Meta:
        verbose_name = 'Картинка'
        verbose_name_plural = 'Картинки'

    def __str__(self):
        return self.movie.title


class Genre(models.Model):
    name = models.CharField(verbose_name='Название', max_length=255)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class UserReview(models.Model):
    user = models.ForeignKey('portal.CustomUser', verbose_name='Пользователь', on_delete=models.CASCADE)
    movie = models.ForeignKey('Movie', verbose_name='Фильм', on_delete=models.CASCADE)
    rating = models.FloatField()

    class Meta:
        verbose_name = 'Отзыв пользователя'
        verbose_name_plural = 'Отзывы пользователя'

    def __str__(self):
        return f'{self.user.username}_{self.movie.title}_{self.rating}'


class DailyRecommendation(models.Model):
    user = models.ForeignKey('portal.CustomUser', verbose_name='Пользователь', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Ежедневная рекомендация'
        verbose_name_plural = 'Ежедневные рекомендации'

    def __str__(self):
        return f'{self.user.username}'


class DailyRecommendedFilm(models.Model):
    recommendation = models.ForeignKey('DailyRecommendation', related_name='movies', verbose_name='рекомендация',
                                       on_delete=models.CASCADE)
    movie = models.ForeignKey('Movie', verbose_name='Фильм дня', related_name='recommended_movies',
                              on_delete=models.CASCADE)
    computed_rating = models.FloatField()

    class Meta:
        verbose_name = 'Ежедневная рекомендация'
        verbose_name_plural = 'Ежедневные рекомендации'

    def __str__(self):
        return f'{self.recommendation.user.username}_{self.movie.title}_{self.computed_rating}'


class FavouriteGenres(models.Model):
    user = models.ForeignKey('portal.CustomUser', verbose_name='Пользователь', on_delete=models.CASCADE)
    genres = models.ManyToManyField('Genre', verbose_name='Жанры')
