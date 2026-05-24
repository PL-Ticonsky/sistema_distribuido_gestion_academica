from django.urls import path

from apps.auditoria.views import AuditoriaDetailView, AuditoriaListView

app_name = "auditoria"

urlpatterns = [
    path("", AuditoriaListView.as_view(), name="auditoria_list"),
    path(
        "<uuid:id_auditoria>/",
        AuditoriaDetailView.as_view(),
        name="auditoria_detail",
    ),
]
