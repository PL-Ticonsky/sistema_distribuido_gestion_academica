from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from django.urls import reverse_lazy

from .forms import EmailAuthenticationForm
from .roles import get_dashboard_options, get_role_labels, get_user_roles


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
    return render(
        request,
        "accounts/dashboard.html",
        {
            "dashboard_options": get_dashboard_options(request.user),
            "role_labels": get_role_labels(request.user),
            "roles": get_user_roles(request.user),
        },
    )
