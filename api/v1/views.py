from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Response as YASG_Response
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from api.v1.authentication import HardTokenAuthentication
from api.v1.serializers import PredictUserFilmsRatingParamsSerializer, DailyRecommendationSerializer, \
    PredictedFilmSerializer, ModifyUserReviewSerializer, UserReviewSerializer
from api.v1.throttles import ThousandPerHourUserThrottle, HundredPerHourUserThrottle
from film_recommender.models import Movie, DailyRecommendedFilm, UserReview


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
                         responses={200: PredictedFilmSerializer(many=True),
                                    400: '{"detail":["specify required field movie_ids",'
                                         '"specify at least one movie_id"]}'})
    def get(self, request, *args, **kwargs):
        serializer = PredictUserFilmsRatingParamsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        movies = Movie.objects.filter(tmdb_id__in=data['movie_ids'])

        Movie.set_predictions_on_movies_for_user(movies, request.user.id)

        serializer = PredictedFilmSerializer(movies, many=True)

        return Response(data=serializer.data, status=HTTP_200_OK)


class UserRatingAPIView(APIView):
    authentication_classes = [HardTokenAuthentication, ]
    throttle_classes = [HundredPerHourUserThrottle, ]

    @swagger_auto_schema(request_body=UserReviewSerializer(many=True),
                         operation_description='Позволяет дать оценку на фильмы',
                         responses={201: '{"detail":"Successfully created"}',
                                    400: '{"detail":["movie with tmdb_id <tmdb_id> does not exist",'
                                         '"rating must be between 1 and 5"]}'})
    def post(self, request, *args, **kwargs):
        data = self._validate_input_data(request.data)
        UserReview.create_user_reviews(request.user.id, data)

        return Response({'detail': 'Successfully created'}, status=HTTP_201_CREATED)

    @swagger_auto_schema(request_body=UserReviewSerializer(many=True),
                         operation_description='Позволяет изменить оценку на фильмы',
                         responses={200: '{"detail":"Successfully updated"}',
                                    400: '{"detail":["movie with tmdb_id <tmdb_id> does not exist",'
                                         '"rating must be between 1 and 5"]}'}

                         )
    def put(self, request, *args, **kwargs):
        data = self._validate_input_data(request.data)
        UserReview.update_user_reviews(request.user.id, data)

        return Response({'detail': 'Successfully updated'}, status=HTTP_200_OK)

    def _validate_input_data(self, data):
        serializer = ModifyUserReviewSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)

        return serializer.validated_data

    @method_decorator(cache_page(60 * 5))
    @method_decorator(vary_on_headers("HTTP_AUTHORIZATION", ))
    @swagger_auto_schema(
        operation_description='Выдает оценённые пользователем фильмы ограничение 100 запросов в час',
        responses={200: UserReviewSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        queryset = UserReview.get_user_reviews(request.user.id)
        serializer = UserReviewSerializer(queryset, many=True)
        return Response(data=serializer.data, status=HTTP_200_OK)
