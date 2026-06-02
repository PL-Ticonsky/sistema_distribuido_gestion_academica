from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView

from apps.accounts.access import RoleRequiredMixin
from apps.reportes.models import (
    EstudianteDetalle,
    GrupoDetalle,
    HomologacionGlobal,
    InscripcionDetalle,
    MatriculaDetalle,
    ProfesorDetalle,
)

REPORT_ROLES = (
    "coordinador",
    "decano",
    "administrativo",
    "superadmin",
)


class ReportesIndexView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = REPORT_ROLES
    template_name = "reportes/index.html"


class ReadOnlyReportListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = REPORT_ROLES
    paginate_by = 25
    filter_fields = ()

    def get_queryset(self):
        queryset = super().get_queryset()
        filters = {}
        for field_name in self.filter_fields:
            value = self.request.GET.get(field_name)
            if value:
                filters[field_name] = value
        if filters:
            queryset = queryset.filter(**filters)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filters"] = {
            field_name: self.request.GET.get(field_name, "")
            for field_name in self.filter_fields
        }
        context["querystring"] = self.request.GET.copy()
        context["querystring"].pop("page", None)
        context["querystring"] = context["querystring"].urlencode()
        return context


class EstudianteListView(ReadOnlyReportListView):
    model = EstudianteDetalle
    template_name = "reportes/estudiantes_list.html"
    context_object_name = "estudiantes"
    filter_fields = (
        "id_facultad",
        "id_programa_academico",
        "estado_estudiante",
    )


class ProfesorListView(ReadOnlyReportListView):
    model = ProfesorDetalle
    template_name = "reportes/profesores_list.html"
    context_object_name = "profesores"
    filter_fields = ("id_facultad",)


class GrupoListView(ReadOnlyReportListView):
    model = GrupoDetalle
    template_name = "reportes/grupos_list.html"
    context_object_name = "grupos"
    filter_fields = (
        "id_facultad",
        "id_programa_academico",
        "id_periodo_academico",
        "estado_grupo",
    )


class InscripcionListView(ReadOnlyReportListView):
    model = InscripcionDetalle
    template_name = "reportes/inscripciones_list.html"
    context_object_name = "inscripciones"
    filter_fields = (
        "id_facultad",
        "id_programa_academico",
        "id_periodo_academico",
        "estado_inscripcion",
    )


class MatriculaListView(ReadOnlyReportListView):
    model = MatriculaDetalle
    template_name = "reportes/matriculas_list.html"
    context_object_name = "matriculas"
    filter_fields = (
        "id_facultad",
        "id_programa_academico",
        "id_periodo_academico",
        "estado_matricula",
    )


class HomologacionListView(ReadOnlyReportListView):
    model = HomologacionGlobal
    template_name = "reportes/homologaciones_list.html"
    context_object_name = "homologaciones"
    filter_fields = ("id_facultad", "estado_homologacion")
