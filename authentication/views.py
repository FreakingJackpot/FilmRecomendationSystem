from django.contrib.auth import authenticate, login
from django.contrib.auth.views import PasswordResetView, LoginView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from authentication.forms import RegistrationForm


class CustomLoginView(LoginView):
    template_name = 'authentication/login.html'
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    pass


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
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password1'],
                                )
            login(request, user)
            return redirect('account:update_user_features')
    else:
        form = RegistrationForm()

    return render(request, 'authentication/registration.html', {'form': form})
