from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from portal.models import CustomUser
from film_recommender.models import Movie, FavouriteGenre, DailyRecommendedFilm
from film_recommender.prediction_service import Predictor

APP_DIR = Path(__file__).resolve().parent.parent.parent


class Command(BaseCommand):

    def handle(self, *args, **options):
        count_with_favourite_genres = settings.TOP_K // 2

        for user_id in CustomUser.objects.filter(id=3).values_list('id', flat=True):
            movies = self._get_movies(user_id)
            predictions = self._predict_movies(user_id, movies, count_with_favourite_genres)
            self._create_recomendation(user_id, predictions)

    def _get_movies(self, user_id):
        genres = FavouriteGenre.objects.filter(user_id=user_id).values_list('genre_id', flat=True)

        base_queryset = Movie.objects.prefetch_related('genres').only('id', 'genres__name').exclude(
            userreview__user_id=user_id).order_by('-rating')

        favourite_genre_movies = base_queryset.filter(genres__in=genres).in_bulk()
        other_movies = base_queryset.in_bulk()

        return {'favourite_genre': favourite_genre_movies, 'other': other_movies}

    def _predict_movies(self, user_id, movies, count_with_favourite_genres):
        predicted_movie_ids = []

        if movies['favourite_genre']:
            predicted_movie_ids.extend(Predictor.get_top_k(
                movies['favourite_genre'].values(),
                user_id,
                count_with_favourite_genres
            ))

        k = settings.TOP_K - len(predicted_movie_ids)
        for movie_id, _ in predicted_movie_ids:
            movies['other'].pop(movie_id)

        predicted_movie_ids.extend(Predictor.get_top_k(
            movies['other'].values(),
            user_id,
            k
        ))

        return predicted_movie_ids

    def _create_recomendation(self, user_id, predictions):
        DailyRecommendedFilm.objects.filter(user_id=user_id).delete()

        recommended_films = []
        for prediction in predictions:
            recommended_films.append(
                DailyRecommendedFilm(user_id=user_id, movie_id=prediction[0], computed_rating=prediction[1])
            )

        DailyRecommendedFilm.objects.bulk_create(recommended_films)
