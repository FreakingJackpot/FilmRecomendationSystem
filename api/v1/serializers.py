from rest_framework import serializers

from film_recommender.models import DailyRecommendedFilm


class DailyRecommendationSerializer(serializers.ModelSerializer):
    tmbd_id = serializers.IntegerField(source='movie.tmbd_id')

    class Meta:
        model = DailyRecommendedFilm
        fields = ['computed_rating', 'tmbd_id', ]


class PredictUserFilmsRatingParamsSerializer(serializers.Serializer):
    movie_ids = serializers.CharField(required=True, help_text='movies tmbd_ids')

    class Meta:
        fields = ['movie_ids', ]

    def validate(self, attrs):
        attrs['movie_ids'] = attrs['movie_ids'].split(',')
        return attrs


class PredictedFilmSerializer(serializers.Serializer):
    tmbd_id = serializers.IntegerField()
    predicted_rating = serializers.FloatField()

    class Meta:
        fields = ['tmbd_id', 'predicted_rating']
