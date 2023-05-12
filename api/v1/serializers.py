
from rest_framework import serializers

from film_recommender.models import DailyRecommendedFilm


class DailyRecommendationSerializer(serializers.ModelSerializer):
    tmdb_id = serializers.IntegerField(source='movie.tmdb_id')

    class Meta:
        model = DailyRecommendedFilm
        fields = ['computed_rating', 'tmdb_id', ]


class PredictUserFilmsRatingParamsSerializer(serializers.Serializer):
    movie_ids = serializers.CharField(required=True, help_text='movies tmdb_ids')

    class Meta:
        fields = ['movie_ids', ]

    def validate(self, attrs):
        attrs['movie_ids'] = attrs['movie_ids'].split(',')
        return attrs


class PredictedFilmSerializer(serializers.Serializer):
    tmdb_id = serializers.IntegerField()
    predicted_rating = serializers.FloatField()

    class Meta:
        fields = ['tmdb_id', 'predicted_rating']
