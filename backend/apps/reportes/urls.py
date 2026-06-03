from django.urls import path

from .views import (
    ConsultaResultadoView,
    ConsultasIndexView,
    EstudiantesDetalleView,
    GruposDetalleView,
    HomologacionesGlobalView,
    InscripcionesDetalleView,
    MatriculasDetalleView,
    ProfesoresDetalleView,
    ReportesIndexView,
    UsuariosGlobalView,
)

app_name = "reportes"

urlpatterns = [
    path("", ReportesIndexView.as_view(), name="index"),
    path("consultas/", ConsultasIndexView.as_view(), name="consultas_index"),
    path(
        "consultas/<int:numero>/",
        ConsultaResultadoView.as_view(),
        name="consulta_resultado",
    ),
    path("usuarios/", UsuariosGlobalView.as_view(), name="usuarios"),
    path("estudiantes/", EstudiantesDetalleView.as_view(), name="estudiantes"),
    path("profesores/", ProfesoresDetalleView.as_view(), name="profesores"),
    path("grupos/", GruposDetalleView.as_view(), name="grupos"),
    path("inscripciones/", InscripcionesDetalleView.as_view(), name="inscripciones"),
    path("matriculas/", MatriculasDetalleView.as_view(), name="matriculas"),
    path("homologaciones/", HomologacionesGlobalView.as_view(), name="homologaciones"),
]
