from django.urls import path

from apps.academica.views import (
    AsignaturaDetailView,
    AsignaturaListView,
    GrupoDetailView,
    GrupoListView,
    InscripcionCancelView,
    InscripcionCreateView,
    InscripcionListView,
    NotaGrupoDetailView,
    NotaGrupoListView,
    NotaInscripcionUpdateView,
    PlanEstudiosListView,
    PreRequisitoListView,
    ProfesorDetailView,
    ProfesorListView,
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
    path("docentes/", ProfesorListView.as_view(), name="profesor_list"),
    path(
        "docentes/<uuid:id_profesor>/",
        ProfesorDetailView.as_view(),
        name="profesor_detail",
    ),
    path("grupos/", GrupoListView.as_view(), name="grupo_list"),
    path("grupos/<uuid:id_grupo>/", GrupoDetailView.as_view(), name="grupo_detail"),
    path("inscripciones/", InscripcionListView.as_view(), name="inscripcion_list"),
    path(
        "inscripciones/crear/",
        InscripcionCreateView.as_view(),
        name="inscripcion_create",
    ),
    path(
        "inscripciones/<uuid:id_inscripcion>/cancelar/",
        InscripcionCancelView.as_view(),
        name="inscripcion_cancel",
    ),
    path("notas/", NotaGrupoListView.as_view(), name="nota_grupo_list"),
    path(
        "notas/grupos/<uuid:id_grupo>/",
        NotaGrupoDetailView.as_view(),
        name="nota_grupo_detail",
    ),
    path(
        "notas/inscripciones/<uuid:id_inscripcion>/editar/",
        NotaInscripcionUpdateView.as_view(),
        name="nota_update",
    ),
]
