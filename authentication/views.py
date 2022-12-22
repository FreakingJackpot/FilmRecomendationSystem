from django.contrib.auth.views import PasswordResetView, LoginView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from authentication.forms import RegistrationForm


class CustomLoginView(LoginView):
    template_name = 'authentication/login.html'


class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'authentication/password_reset_email.html'
    template_name = 'authentication/reset_password_form.html'
    success_url = reverse_lazy("authentication:password_reset_done")


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'authentication/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'authentication/reset_password_form.html'
    success_url = reverse_lazy("authentication:password_reset_complete")


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'authentication/password_reset_complete.html'


def registration(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('authentication:login')
    else:
        form = RegistrationForm()

    return render(request, 'authentication/registration.html', {'form': form})
