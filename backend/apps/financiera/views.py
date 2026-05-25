from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from apps.accounts.access import FINANCIAL_ROLES, RoleRequiredMixin
from apps.accounts.scope import (
    get_administrative_faculty_ids,
    get_program_ids_for_faculties,
    get_student_for_user,
    is_superadmin,
)
from apps.financiera.models import Matricula, Recibo, TarifaMatricula


def filter_financial_queryset_for_user(queryset, user, *, path_prefix=""):
    if is_superadmin(user):
        return queryset

    filtered = queryset.none()
    student = get_student_for_user(user)
    if student:
        student_filter = {f"{path_prefix}estudiante": student}
        filtered = filtered | queryset.filter(**student_filter)

    admin_program_ids = get_program_ids_for_faculties(
        get_administrative_faculty_ids(user),
    )
    if admin_program_ids:
        field_name = f"{path_prefix}tarifa_matricula__programa_academico_id__in"
        program_filter = {
            field_name: admin_program_ids,
        }
        filtered = filtered | queryset.filter(**program_filter)

    return filtered.distinct()


class TarifaMatriculaListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = FINANCIAL_ROLES
    model = TarifaMatricula
    template_name = "financiera/tarifa_list.html"
    context_object_name = "tarifas"

    def get_queryset(self):
        queryset = TarifaMatricula.objects.select_related(
            "programa_academico",
            "programa_academico__facultad",
            "periodo_academico",
        )
        if is_superadmin(self.request.user):
            return queryset
        admin_program_ids = get_program_ids_for_faculties(
            get_administrative_faculty_ids(self.request.user),
        )
        student = get_student_for_user(self.request.user)
        if student:
            admin_program_ids.append(student.programa_academico_id)
        return queryset.filter(programa_academico_id__in=admin_program_ids).distinct()


class ReciboListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = FINANCIAL_ROLES
    model = Recibo
    template_name = "financiera/recibo_list.html"
    context_object_name = "recibos"

    def get_queryset(self):
        queryset = Recibo.objects.select_related(
            "estudiante__usuario",
            "estudiante__programa_academico",
            "tarifa_matricula__programa_academico",
            "tarifa_matricula__periodo_academico",
        )
        return filter_financial_queryset_for_user(queryset, self.request.user)


class ReciboDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    allowed_roles = FINANCIAL_ROLES
    model = Recibo
    template_name = "financiera/recibo_detail.html"
    context_object_name = "recibo"
    pk_url_kwarg = "id_recibo"

    def get_queryset(self):
        queryset = Recibo.objects.select_related(
            "estudiante__usuario",
            "estudiante__programa_academico",
            "tarifa_matricula__programa_academico",
            "tarifa_matricula__periodo_academico",
        )
        return filter_financial_queryset_for_user(queryset, self.request.user)


class MatriculaListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = FINANCIAL_ROLES
    model = Matricula
    template_name = "financiera/matricula_list.html"
    context_object_name = "matriculas"

    def get_queryset(self):
        queryset = Matricula.objects.select_related(
            "recibo__estudiante__usuario",
            "recibo__estudiante__programa_academico",
            "recibo__tarifa_matricula__programa_academico",
            "recibo__tarifa_matricula__periodo_academico",
        )
        return filter_financial_queryset_for_user(
            queryset,
            self.request.user,
            path_prefix="recibo__",
        )


class MatriculaDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    allowed_roles = FINANCIAL_ROLES
    model = Matricula
    template_name = "financiera/matricula_detail.html"
    context_object_name = "matricula"
    pk_url_kwarg = "id_matricula"

    def get_queryset(self):
        queryset = Matricula.objects.select_related(
            "recibo__estudiante__usuario",
            "recibo__estudiante__programa_academico",
            "recibo__tarifa_matricula__programa_academico",
            "recibo__tarifa_matricula__periodo_academico",
        )
        return filter_financial_queryset_for_user(
            queryset,
            self.request.user,
            path_prefix="recibo__",
        )
