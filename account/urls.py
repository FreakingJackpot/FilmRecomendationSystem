from django.urls import path

from account.views import change_email, change_password, manage_favourite_genres,generate_api_token

urlpatterns = [
    path('change_email/', change_email, name='change_email'),
    path('change_password/', change_password, name='change_password'),
    path('manage_favourite_genres/', manage_favourite_genres, name='manage_favourite_genres'),
    path('generate_api_token/', generate_api_token, name='generate_api_token'),
]
