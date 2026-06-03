from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from apps.accounts.access import STRUCTURE_ROLES, RoleRequiredMixin
from apps.accounts.access_context import get_access_context
from apps.estructura.models import (
    Asignatura,
    Facultad,
    PeriodoAcademico,
    ProgramaAcademico,
)


class FacultadListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = STRUCTURE_ROLES
    model = Facultad
    template_name = "estructura/facultad_list.html"
    context_object_name = "facultades"
    paginate_by = 25

    def get_queryset(self):
        context = get_access_context(self.request.user)
        queryset = Facultad.objects.all()
        if context.is_superadmin:
            return queryset
        return queryset.filter(id_facultad__in=context.faculty_ids)


class FacultadDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    allowed_roles = STRUCTURE_ROLES
    model = Facultad
    template_name = "estructura/facultad_detail.html"
    context_object_name = "facultad"
    pk_url_kwarg = "id_facultad"

    def get_queryset(self):
        context = get_access_context(self.request.user)
        queryset = Facultad.objects.prefetch_related("programas")
        if context.is_superadmin:
            return queryset
        return queryset.filter(id_facultad__in=context.faculty_ids)


class ProgramaListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = STRUCTURE_ROLES
    model = ProgramaAcademico
    template_name = "estructura/programa_list.html"
    context_object_name = "programas"
    paginate_by = 25

    def get_queryset(self):
        context = get_access_context(self.request.user)
        queryset = ProgramaAcademico.objects.select_related("facultad").order_by(
            "nombre_programa",
        )
        if context.is_superadmin:
            return queryset
        return queryset.filter(id_programa_academico__in=context.program_ids)


class PeriodoAcademicoListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = STRUCTURE_ROLES
    model = PeriodoAcademico
    template_name = "estructura/periodo_list.html"
    context_object_name = "periodos"
    paginate_by = 25


class AsignaturaListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = STRUCTURE_ROLES
    model = Asignatura
    template_name = "estructura/asignatura_list.html"
    context_object_name = "asignaturas"
    paginate_by = 25
