from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from apps.accounts.access import STRUCTURE_ROLES, RoleRequiredMixin
from apps.accounts.scope import get_visible_faculty_ids, get_visible_program_ids
from apps.estructura.models import Facultad, PeriodoAcademico, ProgramaAcademico


class FacultadListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = STRUCTURE_ROLES
    model = Facultad
    template_name = "estructura/facultad_list.html"
    context_object_name = "facultades"

    def get_queryset(self):
        faculty_ids = get_visible_faculty_ids(self.request.user)
        queryset = Facultad.objects.all()
        if faculty_ids is None:
            return queryset
        return queryset.filter(id_facultad__in=faculty_ids)


class FacultadDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    allowed_roles = STRUCTURE_ROLES
    model = Facultad
    template_name = "estructura/facultad_detail.html"
    context_object_name = "facultad"
    pk_url_kwarg = "id_facultad"

    def get_queryset(self):
        faculty_ids = get_visible_faculty_ids(self.request.user)
        queryset = Facultad.objects.prefetch_related("programas")
        if faculty_ids is None:
            return queryset
        return queryset.filter(id_facultad__in=faculty_ids)


class ProgramaListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = STRUCTURE_ROLES
    model = ProgramaAcademico
    template_name = "estructura/programa_list.html"
    context_object_name = "programas"

    def get_queryset(self):
        program_ids = get_visible_program_ids(self.request.user)
        queryset = ProgramaAcademico.objects.select_related("facultad")
        if program_ids is None:
            return queryset
        return queryset.filter(id_programa_academico__in=program_ids)


class PeriodoAcademicoListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = STRUCTURE_ROLES
    model = PeriodoAcademico
    template_name = "estructura/periodo_list.html"
    context_object_name = "periodos"
