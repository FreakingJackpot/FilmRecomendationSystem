from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.status import HTTP_200_OK

from api.v1.authentication import HardTokenAuthentication
from api.v1.serializers import PredictUserFilmsRatingParamsSerializer, DailyRecommendationSerializer, \
    PredictedFilmSerializer
from api.v1.throttles import ThousandPerHourUserThrottle
from film_recommender.models import Movie, DailyRecommendedFilm


class DailyRecommendAPIView(ListAPIView):
    authentication_classes = [HardTokenAuthentication, ]
    model = DailyRecommendedFilm
    serializer_class = DailyRecommendationSerializer

    @method_decorator(cache_page(60 * 60 * 2))
    @method_decorator(vary_on_headers("HTTP_AUTHORIZATION", ))
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        queryset = self.model.objects.filter(user=user).select_related('movie')
        return queryset


class PredictUserFilmsRatingAPIView(APIView):
    authentication_classes = [HardTokenAuthentication, ]
    throttle_classes = [ThousandPerHourUserThrottle, ]

    @method_decorator(cache_page(60 * 30))
    @method_decorator(vary_on_headers("HTTP_AUTHORIZATION", ))
    @swagger_auto_schema(query_serializer=PredictUserFilmsRatingParamsSerializer(),
                         operation_description='Предсказывает рейтинги фильмов, ограничение 1000 запросов в час',
                         responses={200: PredictedFilmSerializer(many=True)})
    def get(self, request, format=None):
        serializer = PredictUserFilmsRatingParamsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        movies = Movie.objects.filter(tmdb_id__in=data['movie_ids'])

        Movie.set_predictions_on_movies_for_user(movies, request.user.id)

        serializer = PredictedFilmSerializer(data=movies, many=True)
        serializer.is_valid()

        return Response(data=serializer.data, status=HTTP_200_OK)
