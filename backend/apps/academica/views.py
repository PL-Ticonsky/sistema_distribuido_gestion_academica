from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import ListView, View

from apps.accounts.access import (
    STUDENT_ROLES,
    TEACHING_ROLES,
    RoleRequiredMixin,
)
from apps.estructura.models import Asignatura
from apps.reportes.models import (
    EstudianteDetalle,
    GrupoDetalle,
    InscripcionDetalle,
    ProfesorDetalle,
)

ACADEMIC_READ_ROLES = (*STUDENT_ROLES, "docente")
READ_ONLY_MESSAGE = "La escritura academica distribuida aun no esta habilitada."


class AcademicReportListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    paginate_by = 25
    filters = ()

    def get_queryset(self):
        queryset = super().get_queryset()
        for field in self.filters:
            value = self.request.GET.get(field)
            if value:
                queryset = queryset.filter(**{field: value})
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_filters"] = {
            field: self.request.GET.get(field, "") for field in self.filters
        }
        return context


class AsignaturaListView(AcademicReportListView):
    allowed_roles = ACADEMIC_READ_ROLES
    model = Asignatura
    template_name = "academica/asignatura_list.html"
    context_object_name = "asignaturas"
    filters = ("estado",)


class EstudianteListView(AcademicReportListView):
    allowed_roles = STUDENT_ROLES
    model = EstudianteDetalle
    template_name = "academica/estudiante_list.html"
    context_object_name = "estudiantes"
    filters = (
        "id_facultad",
        "nombre_facultad",
        "id_programa_academico",
        "nombre_programa",
        "estado_estudiante",
    )


class ProfesorListView(AcademicReportListView):
    allowed_roles = TEACHING_ROLES
    model = ProfesorDetalle
    template_name = "academica/profesor_list.html"
    context_object_name = "profesores"
    filters = ("id_facultad", "nombre_facultad", "categoria", "vinculacion")


class GrupoListView(AcademicReportListView):
    allowed_roles = TEACHING_ROLES
    model = GrupoDetalle
    template_name = "academica/grupo_list.html"
    context_object_name = "grupos"
    filters = (
        "id_facultad",
        "nombre_facultad",
        "id_programa_academico",
        "nombre_programa",
        "id_periodo_academico",
        "estado_grupo",
    )


class InscripcionListView(AcademicReportListView):
    allowed_roles = ACADEMIC_READ_ROLES
    model = InscripcionDetalle
    template_name = "academica/inscripcion_list.html"
    context_object_name = "inscripciones"
    filters = (
        "id_facultad",
        "nombre_facultad",
        "id_programa_academico",
        "nombre_programa",
        "id_periodo_academico",
        "estado_inscripcion",
    )


class ReadOnlyRedirectView(LoginRequiredMixin, View):
    redirect_url_name = "academica:inscripcion_list"

    def get(self, request, *args, **kwargs):
        messages.warning(request, READ_ONLY_MESSAGE)
        return redirect(self.redirect_url_name)

    def post(self, request, *args, **kwargs):
        messages.warning(request, READ_ONLY_MESSAGE)
        return redirect(self.redirect_url_name)


class AsignaturaDetailView(ReadOnlyRedirectView):
    redirect_url_name = "academica:asignatura_list"


class ProfesorDetailView(ReadOnlyRedirectView):
    redirect_url_name = "academica:profesor_list"


class GrupoDetailView(ReadOnlyRedirectView):
    redirect_url_name = "academica:grupo_list"


class PlanEstudiosListView(ReadOnlyRedirectView):
    redirect_url_name = "academica:asignatura_list"


class PreRequisitoListView(ReadOnlyRedirectView):
    redirect_url_name = "academica:asignatura_list"


class EstudianteCreateView(ReadOnlyRedirectView):
    redirect_url_name = "academica:estudiante_list"


class InscripcionCreateView(ReadOnlyRedirectView):
    redirect_url_name = "academica:inscripcion_list"


class InscripcionCancelView(ReadOnlyRedirectView):
    redirect_url_name = "academica:inscripcion_list"


class NotaGrupoListView(ReadOnlyRedirectView):
    redirect_url_name = "academica:grupo_list"


class NotaGrupoDetailView(ReadOnlyRedirectView):
    redirect_url_name = "academica:grupo_list"


class NotaInscripcionUpdateView(ReadOnlyRedirectView):
    redirect_url_name = "academica:inscripcion_list"
