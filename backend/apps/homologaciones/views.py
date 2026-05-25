from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from apps.accounts.access import HOMOLOGATION_ROLES, RoleRequiredMixin
from apps.accounts.scope import (
    get_professor_for_user,
    get_student_for_user,
    get_visible_program_ids,
    is_superadmin,
)
from apps.homologaciones.models import Homologacion


def filter_homologaciones_for_user(queryset, user):
    if is_superadmin(user):
        return queryset

    filtered = queryset.none()
    student = get_student_for_user(user)
    if student:
        filtered = filtered | queryset.filter(estudiante=student)

    professor = get_professor_for_user(user)
    if professor:
        filtered = filtered | queryset.filter(profesor_evaluador=professor)

    program_ids = get_visible_program_ids(user)
    if program_ids:
        filtered = filtered | queryset.filter(
            programa_asignatura__programa_academico_id__in=program_ids,
        )

    return filtered.distinct()


class HomologacionListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = HOMOLOGATION_ROLES
    model = Homologacion
    template_name = "homologaciones/homologacion_list.html"
    context_object_name = "homologaciones"

    def get_queryset(self):
        queryset = Homologacion.objects.select_related(
            "estudiante__usuario",
            "estudiante__programa_academico",
            "profesor_evaluador__usuario",
            "programa_asignatura__asignatura",
            "programa_asignatura__programa_academico",
        )
        return filter_homologaciones_for_user(queryset, self.request.user)


class HomologacionDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    allowed_roles = HOMOLOGATION_ROLES
    model = Homologacion
    template_name = "homologaciones/homologacion_detail.html"
    context_object_name = "homologacion"
    pk_url_kwarg = "id_homologacion"

    def get_queryset(self):
        queryset = Homologacion.objects.select_related(
            "estudiante__usuario",
            "estudiante__programa_academico",
            "profesor_evaluador__usuario",
            "programa_asignatura__asignatura",
            "programa_asignatura__programa_academico",
        )
        return filter_homologaciones_for_user(queryset, self.request.user)
