from django.urls import path

from apps.indicadores.views import (
    IndicadorDetailView,
    IndicadorListView,
    MiIndicadorView,
)

app_name = "indicadores"

urlpatterns = [
    path("", IndicadorListView.as_view(), name="indicador_list"),
    path("mis-indicadores/", MiIndicadorView.as_view(), name="mi_indicador"),
    path(
        "estudiantes/<uuid:id_estudiante>/",
        IndicadorDetailView.as_view(),
        name="indicador_detail",
    ),
]
