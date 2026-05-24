from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from django.urls import reverse_lazy

from .forms import EmailAuthenticationForm


class EmailLoginView(LoginView):
    authentication_form = EmailAuthenticationForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("accounts:dashboard")


class EmailLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")


@login_required
def dashboard(request):
    return render(request, "accounts/dashboard.html")
