from django.urls import path

from .views import EmailLoginView, EmailLogoutView, dashboard

app_name = "accounts"

urlpatterns = [
    path("login/", EmailLoginView.as_view(), name="login"),
    path("logout/", EmailLogoutView.as_view(), name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
]
