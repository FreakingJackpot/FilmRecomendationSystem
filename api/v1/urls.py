from django.urls import path

from .views import DailyRecommendAPIView, PredictUserFilmsRatingAPIView, UserRatingAPIView

urlpatterns = [
    path('daily-recommends/', DailyRecommendAPIView.as_view(), name='daily-recommends'),
    path('predictor/', PredictUserFilmsRatingAPIView.as_view(), name='predictor'),
    path('reviews/', UserRatingAPIView.as_view(), name='reviews'),
]
