from django.urls import path

from apps.academica.views import (
    AsignaturaDetailView,
    AsignaturaListView,
    GrupoDetailView,
    GrupoListView,
    InscripcionListView,
    PlanEstudiosListView,
    PreRequisitoListView,
)

app_name = "academica"

urlpatterns = [
    path("asignaturas/", AsignaturaListView.as_view(), name="asignatura_list"),
    path(
        "asignaturas/<str:cod_asignatura>/",
        AsignaturaDetailView.as_view(),
        name="asignatura_detail",
    ),
    path("planes/", PlanEstudiosListView.as_view(), name="plan_estudios_list"),
    path("prerrequisitos/", PreRequisitoListView.as_view(), name="prerequisito_list"),
    path("grupos/", GrupoListView.as_view(), name="grupo_list"),
    path("grupos/<uuid:id_grupo>/", GrupoDetailView.as_view(), name="grupo_detail"),
    path("inscripciones/", InscripcionListView.as_view(), name="inscripcion_list"),
]
