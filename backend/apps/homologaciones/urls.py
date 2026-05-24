from django.urls import path

from apps.homologaciones.views import HomologacionDetailView, HomologacionListView

app_name = "homologaciones"

urlpatterns = [
    path("", HomologacionListView.as_view(), name="homologacion_list"),
    path(
        "<uuid:id_homologacion>/",
        HomologacionDetailView.as_view(),
        name="homologacion_detail",
    ),
]
