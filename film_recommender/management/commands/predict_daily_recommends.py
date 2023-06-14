from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.core.management.base import BaseCommand

from account.models import CustomUser
from film_recommender.models import Movie, FavouriteGenre, DailyRecommendedFilm
from film_recommender.prediction_service import Predictor
from film_recommender.services import chunks

APP_DIR = Path(__file__).resolve().parent.parent.parent


class Command(BaseCommand):
    _users_chunk = 500
    _butch_size = 500
    _count_with_favourite_genres = settings.TOP_K // 2

    def handle(self, *args, **options):
        user_ids = tuple(CustomUser.objects.filter(id=611).values_list('id', flat=True).iterator())
        with ThreadPoolExecutor() as executor:
            for chunk in chunks(user_ids, 3):
                recommendations = []
                for result in executor.map(self._get_user_recommendations, chunk):
                    recommendations.extend(result)
                DailyRecommendedFilm.objects.filter(user_id__in=chunk).delete()
                DailyRecommendedFilm.objects.bulk_create(recommendations, batch_size=self._butch_size)

    def _get_user_recommendations(self, user_id):
        movie_ids = self._get_movie_ids(user_id)
        predictions = self._predict_movie_ids(user_id, movie_ids, self._count_with_favourite_genres)
        return self._create_user_recomendations(user_id, predictions)

    def _get_movie_ids(self, user_id):
        genre_ids = FavouriteGenre.objects.filter(user_id=user_id).values_list('genre_id', flat=True)

        base_queryset = Movie.objects.exclude(userreview__user_id=user_id).order_by('-rating')
        favourite_genre_movies = base_queryset.filter(genres__id__in=genre_ids).distinct().values_list('id', flat=True)
        other_movies = base_queryset.values_list('id', flat=True)

        return {'favourite_genre': tuple(favourite_genre_movies), 'other': list(other_movies)}

    def _predict_movie_ids(self, user_id, movie_ids, count_with_favourite_genres):
        predicted_movies = []

        if movie_ids['favourite_genre']:
            predicted_movies.extend(Predictor.get_top_k(
                user_id,
                movie_ids['favourite_genre'],
                count_with_favourite_genres
            ))

        k = settings.TOP_K - len(predicted_movies)
        for prediction in predicted_movies:
            movie_ids['other'].remove(prediction['movie_id'])

        predicted_movies.extend(Predictor.get_top_k(
            user_id,
            movie_ids['other'],
            k
        ))

        return predicted_movies

    def _create_user_recomendations(self, user_id, predictions):
        recommended_films = []
        for prediction in predictions:
            recommended_films.append(
                DailyRecommendedFilm(user_id=user_id,
                                     movie_id=prediction['movie_id'],
                                     predicted_rating=prediction['rating'])
            )

        return recommended_films
