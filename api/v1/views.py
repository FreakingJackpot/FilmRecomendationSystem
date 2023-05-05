from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.status import HTTP_200_OK

from api.v1.authentication import HardTokenAuthentication
from api.v1.serializers import PredictUserFilmsRatingParamsSerializer, DailyRecommendationSerializer, \
    PredictedFilmSerializer
from api.v1.throttles import OncePerHourUserThrottle, ThousandPerHourUserThrottle
from film_recommender.models import Movie, DailyRecommendedFilm


class DailyRecommendAPIView(ListAPIView):
    authentication_classes = [HardTokenAuthentication, ]
    throttle_classes = [OncePerHourUserThrottle, ]
    model = DailyRecommendedFilm
    serializer_class = DailyRecommendationSerializer

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        try:
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            obj = None
        return obj

    def get_queryset(self):
        user = self.request.user
        queryset = self.model.objects.filter(recommendation__user=user).select_related('movie')
        return queryset


class PredictUserFilmsRatingAPIView(APIView):
    authentication_classes = [HardTokenAuthentication, ]
    throttle_classes = [ThousandPerHourUserThrottle, ]

    @swagger_auto_schema(query_serializer=PredictUserFilmsRatingParamsSerializer(),
                         responses={200: PredictedFilmSerializer(many=True)})
    def get(self, request, format=None):
        serializer = PredictUserFilmsRatingParamsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        movies = Movie.objects.filter(tmbd_id__in=data['movie_ids'])

        Movie.set_predictions_on_movies_for_user(movies, request.user.id)

        serializer = PredictedFilmSerializer(data=movies, many=True)
        serializer.is_valid()

        return Response(data=serializer.data, status=HTTP_200_OK)
