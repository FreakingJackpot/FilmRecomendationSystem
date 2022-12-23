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
    def get_10_most_rated_without_review(cls, user_id):
        return cls.get_most_related_without_review(user_id)[:10]

    @classmethod
    def get_most_related_without_review(cls, user_id):
        return cls.objects.prefetch_related('images').exclude(userreview__user_id=user_id).order_by('-rating')

    @classmethod
    def get_10_most_rated_without_review_for_each_genre(cls, user_id, exclude_movie_ids):
        genres_recommendations = {}
        for genre in Genre.objects.all():
            queryset = cls.get_most_rated_without_review_for_genre(user_id, genre)
            if exclude_movie_ids:
                queryset = queryset.exclude(id__in=exclude_movie_ids)

            genres_recommendations[genre.name] = queryset[:10]

        return genres_recommendations

    @classmethod
    def get_most_rated_without_review_for_genre(cls, user_id, genre):
        return cls.objects.prefetch_related('images').filter(genres=genre).exclude(
            userreview__user_id=user_id).order_by('-rating')


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
    movies = models.ManyToManyField('Movie', verbose_name='Фильмы дня', )

    class Meta:
        verbose_name = 'Ежедневная рекомендация'
        verbose_name_plural = 'Ежедневные рекомендации'

    def __str__(self):
        return f'{self.user.username}'


class DailyRecommendedFilm(models.Model):
    recommendation = models.ForeignKey('DailyRecommendation', verbose_name='рекомендация', on_delete=models.CASCADE)
    movie = models.ForeignKey('Movie', verbose_name='Фильм дня', on_delete=models.CASCADE)
    computed_rating = models.FloatField()

    class Meta:
        verbose_name = 'Ежедневная рекомендация'
        verbose_name_plural = 'Ежедневные рекомендации'

    def __str__(self):
        return f'{self.recommendation.user.username}_{self.movie.title}_{self.computed_rating}'


class FavouriteGenres(models.Model):
    user = models.ForeignKey('portal.CustomUser', verbose_name='Пользователь', on_delete=models.CASCADE)
    genres = models.ManyToManyField('Genre', verbose_name='Жанры')
