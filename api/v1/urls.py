from django.urls import path

from .views import DailyRecommendAPIView, PredictUserFilmsRatingAPIView

urlpatterns = [
    path('daily-recommends/', DailyRecommendAPIView.as_view(), name='login'),
    path('predict-films-rating/', PredictUserFilmsRatingAPIView.as_view(), name='logout'),
]
