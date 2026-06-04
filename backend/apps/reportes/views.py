from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import ListView, TemplateView

from apps.accounts.access import REPORT_ROLES, RoleRequiredMixin
from apps.accounts.access_context import (
    filter_estudiantes_for_user,
    filter_grupos_for_user,
    filter_homologaciones_for_user,
    filter_inscripciones_for_user,
    filter_matriculas_for_user,
    filter_profesores_for_user,
)
from apps.reportes.services import ejecutar_consulta, listar_consultas

from .models import (
    EstudianteDetalle,
    GrupoDetalle,
    HomologacionGlobal,
    InscripcionDetalle,
    MatriculaDetalle,
    ProfesorDetalle,
    UsuarioGlobal,
)


class ReportesIndexView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = REPORT_ROLES
    template_name = "reportes/index.html"


class ConsultasIndexView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = REPORT_ROLES
    template_name = "reportes/consultas_index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["consultas"] = listar_consultas()
        return context


class ConsultaResultadoView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = REPORT_ROLES
    template_name = "reportes/consulta_resultado.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        numero = self.kwargs["numero"]
        consulta, columns, rows = ejecutar_consulta(numero)
        if consulta is None:
            raise Http404("Consulta no encontrada.")
        context["consulta"] = consulta
        context["columns"] = columns
        context["rows"] = rows
        return context


class ReporteListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = REPORT_ROLES
    paginate_by = 25
    template_name = "reportes/list.html"

    title = ""
    columns = ()
    access_filter = None

    def get_queryset(self):
        queryset = self.model.objects.all()
        if self.access_filter is not None:
            queryset = self.access_filter(queryset, self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["columns"] = self.columns
        return context


class UsuariosGlobalView(ReporteListView):
    model = UsuarioGlobal
    title = "Usuarios globales"
    columns = (
        ("nombre", "Nombre"),
        ("correo", "Correo"),
        ("tipo_de_documento", "Tipo doc."),
        ("numero_de_documento", "Documento"),
        ("is_active", "Activo"),
    )


class EstudiantesDetalleView(ReporteListView):
    model = EstudianteDetalle
    title = "Estudiantes"
    access_filter = staticmethod(filter_estudiantes_for_user)
    columns = (
        ("nodo_origen", "Nodo"),
        ("estudiante", "Estudiante"),
        ("correo", "Correo"),
        ("nombre_facultad", "Facultad"),
        ("nombre_programa", "Programa"),
        ("estado_estudiante", "Estado"),
    )


class ProfesoresDetalleView(ReporteListView):
    model = ProfesorDetalle
    title = "Profesores"
    access_filter = staticmethod(filter_profesores_for_user)
    columns = (
        ("nodo_origen", "Nodo"),
        ("profesor", "Profesor"),
        ("correo", "Correo"),
        ("nombre_facultad", "Facultad"),
        ("categoria", "Categoria"),
        ("vinculacion", "Vinculacion"),
    )


class GruposDetalleView(ReporteListView):
    model = GrupoDetalle
    title = "Grupos"
    access_filter = staticmethod(filter_grupos_for_user)
    columns = (
        ("nodo_origen", "Nodo"),
        ("codigo_grupo", "Grupo"),
        ("nombre_asignatura", "Asignatura"),
        ("nombre_programa", "Programa"),
        ("nombre_facultad", "Facultad"),
        ("profesor", "Profesor"),
        ("cupo_maximo", "Cupo"),
    )


class InscripcionesDetalleView(ReporteListView):
    model = InscripcionDetalle
    title = "Inscripciones"
    access_filter = staticmethod(filter_inscripciones_for_user)
    columns = (
        ("nodo_origen", "Nodo"),
        ("estudiante", "Estudiante"),
        ("nombre_asignatura", "Asignatura"),
        ("codigo_grupo", "Grupo"),
        ("profesor", "Profesor"),
        ("nota_final", "Nota"),
        ("estado_inscripcion", "Estado"),
    )


class MatriculasDetalleView(ReporteListView):
    model = MatriculaDetalle
    title = "Matriculas"
    access_filter = staticmethod(filter_matriculas_for_user)
    columns = (
        ("nodo_origen", "Nodo"),
        ("estudiante", "Estudiante"),
        ("nombre_programa", "Programa"),
        ("id_periodo_academico", "Periodo"),
        ("estado_matricula", "Matricula"),
        ("estado_pago", "Pago"),
        ("valor_pagado", "Valor"),
    )


class HomologacionesGlobalView(ReporteListView):
    model = HomologacionGlobal
    title = "Homologaciones"
    access_filter = staticmethod(filter_homologaciones_for_user)
    columns = (
        ("nodo_origen", "Nodo"),
        ("asignatura_origen", "Asignatura origen"),
        ("institucion_origen", "Institucion"),
        ("estado_homologacion", "Estado"),
        ("fecha_solicitud", "Solicitud"),
        ("fecha_respuesta", "Respuesta"),
        ("nota_obtenida", "Nota"),
    )
