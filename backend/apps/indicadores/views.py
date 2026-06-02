from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView

from apps.academica.models import Estudiante
from apps.accounts.access import INDICATOR_ROLES, RoleRequiredMixin
from apps.accounts.roles import get_user_roles
from apps.accounts.scope import (
    get_professor_for_user,
    get_student_for_user,
    get_visible_program_ids,
    is_superadmin,
)
from apps.indicadores.services import calculate_student_indicators


def get_indicator_students_queryset(user):
    queryset = Estudiante.objects.select_related(
        "usuario",
        "programa_academico",
        "programa_academico__facultad",
    )
    if is_superadmin(user):
        return queryset

    roles = set(get_user_roles(user))
    filtered = queryset.none()

    if "estudiante" in roles:
        student = get_student_for_user(user)
        if student:
            filtered = filtered | queryset.filter(pk=student.pk)

    if "docente" in roles:
        professor = get_professor_for_user(user)
        if professor:
            filtered = filtered | queryset.filter(
                inscripciones__grupo__profesor=professor,
            )

    program_ids = get_visible_program_ids(user)
    if program_ids:
        filtered = filtered | queryset.filter(programa_academico_id__in=program_ids)

    return filtered.distinct()


class IndicadorListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = INDICATOR_ROLES
    model = Estudiante
    template_name = "indicadores/indicador_list.html"
    context_object_name = "indicadores"

    def get_queryset(self):
        return get_indicator_students_queryset(self.request.user).order_by(
            "programa_academico__nombre_programa",
            "usuario__nombre",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["indicadores"] = [
            calculate_student_indicators(student) for student in context["indicadores"]
        ]
        return context


class MiIndicadorView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    allowed_roles = ("estudiante", "superadmin")
    model = Estudiante
    template_name = "indicadores/indicador_detail.html"
    context_object_name = "estudiante"

    def dispatch(self, request, *args, **kwargs):
        student = get_student_for_user(request.user)
        if not student:
            messages.error(
                request,
                "Tu usuario no tiene un registro de estudiante asociado.",
            )
            return redirect("accounts:dashboard")
        self.student = student
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.student

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["indicador"] = calculate_student_indicators(self.object)
        return context


class IndicadorDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    allowed_roles = INDICATOR_ROLES
    model = Estudiante
    template_name = "indicadores/indicador_detail.html"
    context_object_name = "estudiante"
    pk_url_kwarg = "id_estudiante"

    def get_object(self, queryset=None):
        queryset = get_indicator_students_queryset(self.request.user)
        return get_object_or_404(queryset, pk=self.kwargs["id_estudiante"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["indicador"] = calculate_student_indicators(self.object)
        return context
