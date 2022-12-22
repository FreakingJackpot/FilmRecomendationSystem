from django.urls import path

from authentication.views import CustomLoginView, CustomPasswordResetView, CustomPasswordResetDoneView, \
    CustomPasswordResetConfirmView, registration, CustomPasswordResetCompleteView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('reset-password/', CustomPasswordResetView.as_view(), name='reset_password'),
    path('reset-password-done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset/complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('registration/', registration, name='registration'),

]
