from django.urls import path

from apps.estructura.views import (
    FacultadDetailView,
    FacultadListView,
    PeriodoAcademicoListView,
    ProgramaListView,
)

app_name = "estructura"

urlpatterns = [
    path("facultades/", FacultadListView.as_view(), name="facultad_list"),
    path(
        "facultades/<str:id_facultad>/",
        FacultadDetailView.as_view(),
        name="facultad_detail",
    ),
    path("programas/", ProgramaListView.as_view(), name="programa_list"),
    path("periodos/", PeriodoAcademicoListView.as_view(), name="periodo_list"),
]
