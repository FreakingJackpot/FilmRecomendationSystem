from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from film_recommender.models import DailyRecommendedFilm, Movie, UserReview


class DailyRecommendationSerializer(serializers.ModelSerializer):
    tmdb_id = serializers.IntegerField(source='movie.tmdb_id')

    class Meta:
        model = DailyRecommendedFilm
        fields = ['predicted_rating', 'tmdb_id', ]


class PredictUserFilmsRatingParamsSerializer(serializers.Serializer):
    movie_ids = serializers.CharField(required=True, help_text='movies tmdb_ids')

    class Meta:
        fields = ['movie_ids', ]

    def validate(self, attrs):
        errors = []
        if isinstance(attrs['movie_ids'], str):
            attrs['movie_ids'] = attrs['movie_ids'].split(',')
        else:
            errors.append('specify required field movie_ids')

        if not attrs['movie_ids']:
            errors.append('specify at least one movie_id')

        if errors:
            raise ValidationError({'detail': errors})

        return attrs


class PredictedFilmSerializer(serializers.Serializer):
    tmdb_id = serializers.IntegerField()
    predicted_rating = serializers.FloatField()

    class Meta:
        fields = ['tmdb_id', 'predicted_rating']


class ModifyUserReviewSerializer(serializers.Serializer):
    tmdb_id = serializers.IntegerField()
    rating = serializers.FloatField()

    class Meta:
        fields = ['tmdb_id', 'rating', ]

    def validate(self, attrs):
        errors = []
        if not Movie.objects.filter(tmdb_id=attrs['tmdb_id']).exists():
            errors.append(f'movie with tmdb_id {attrs["tmdb_id"]} does not exist')
        if not 5 >= attrs['rating'] >= 1:
            errors.append(f'rating must be between 1 and 5')

        if errors:
            raise ValidationError({'detail': errors})
        return attrs


class UserReviewSerializer(serializers.ModelSerializer):
    tmdb_id = serializers.IntegerField(source='movie.tmdb_id')
    rating = serializers.FloatField()

    class Meta:
        model = UserReview
        fields = ['tmdb_id', 'rating', ]
