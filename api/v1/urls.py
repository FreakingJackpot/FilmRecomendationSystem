from django.urls import path

from .views import DailyRecommendAPIView, PredictUserFilmsRatingAPIView

urlpatterns = [
    path('daily-recommends/', DailyRecommendAPIView.as_view(), name='daily-recommends'),
    path('predictor/', PredictUserFilmsRatingAPIView.as_view(), name='predictor'),
]
