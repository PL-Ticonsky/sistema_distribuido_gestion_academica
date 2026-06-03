from django.urls import path

from apps.academica.views import (
    AsignaturaDetailView,
    AsignaturaListView,
    EstudianteCreateView,
    EstudianteDeactivateView,
    EstudianteDetailView,
    EstudianteListView,
    EstudianteUpdateView,
    GrupoCancelView,
    GrupoCreateView,
    GrupoDetailView,
    GrupoListView,
    GrupoUpdateView,
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
    path("estudiantes/", EstudianteListView.as_view(), name="estudiante_list"),
    path(
        "estudiantes/crear/",
        EstudianteCreateView.as_view(),
        name="estudiante_create",
    ),
    path(
        "estudiantes/agregar/",
        EstudianteCreateView.as_view(),
        name="estudiante_create_alias",
    ),
    path(
        "estudiantes/<uuid:id_estudiante>/",
        EstudianteDetailView.as_view(),
        name="estudiante_detail",
    ),
    path(
        "estudiantes/<uuid:id_estudiante>/editar/",
        EstudianteUpdateView.as_view(),
        name="estudiante_update",
    ),
    path(
        "estudiantes/<uuid:id_estudiante>/desactivar/",
        EstudianteDeactivateView.as_view(),
        name="estudiante_deactivate",
    ),
    path("docentes/", ProfesorListView.as_view(), name="profesor_list"),
    path("profesores/", ProfesorListView.as_view(), name="profesor_list_alias"),
    path(
        "docentes/<uuid:id_profesor>/",
        ProfesorDetailView.as_view(),
        name="profesor_detail",
    ),
    path("grupos/", GrupoListView.as_view(), name="grupo_list"),
    path("grupos/crear/", GrupoCreateView.as_view(), name="grupo_create"),
    path("grupos/<uuid:id_grupo>/", GrupoDetailView.as_view(), name="grupo_detail"),
    path(
        "grupos/<uuid:id_grupo>/editar/",
        GrupoUpdateView.as_view(),
        name="grupo_update",
    ),
    path(
        "grupos/<uuid:id_grupo>/cancelar/",
        GrupoCancelView.as_view(),
        name="grupo_cancel",
    ),
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
