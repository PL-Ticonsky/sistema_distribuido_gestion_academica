from django.urls import path

from apps.reportes.views import (
    EstudianteListView,
    GrupoListView,
    HomologacionListView,
    InscripcionListView,
    MatriculaListView,
    ProfesorListView,
    ReportesIndexView,
)

app_name = "reportes"

urlpatterns = [
    path("", ReportesIndexView.as_view(), name="index"),
    path("estudiantes/", EstudianteListView.as_view(), name="estudiante_list"),
    path("profesores/", ProfesorListView.as_view(), name="profesor_list"),
    path("grupos/", GrupoListView.as_view(), name="grupo_list"),
    path("inscripciones/", InscripcionListView.as_view(), name="inscripcion_list"),
    path("matriculas/", MatriculaListView.as_view(), name="matricula_list"),
    path("homologaciones/", HomologacionListView.as_view(), name="homologacion_list"),
]
