from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.accounts.access import HOMOLOGATION_ROLES, RoleRequiredMixin
from apps.accounts.roles import get_user_roles
from apps.accounts.scope import (
    get_coordinated_program_ids,
    get_professor_for_user,
    get_student_for_user,
    get_visible_program_ids,
    is_superadmin,
)
from apps.homologaciones.forms import (
    HomologacionAsignarEvaluadorForm,
    HomologacionEvaluarForm,
    HomologacionSolicitudForm,
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        roles = set(get_user_roles(self.request.user))
        context["can_create_homologacion"] = (
            "estudiante" in roles
            and not is_superadmin(
                self.request.user,
            )
        )
        context["can_manage_homologaciones"] = is_superadmin(
            self.request.user,
        ) or bool(roles.intersection({"docente", "coordinador"}))
        return context


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        homologacion = self.object
        user = self.request.user
        roles = set(get_user_roles(user))
        student = get_student_for_user(user)
        professor = get_professor_for_user(user)
        coordinated_program_ids = get_coordinated_program_ids(user)

        context["can_cancel_homologacion"] = (
            student == homologacion.estudiante
            and homologacion.estado_homologacion
            == Homologacion.EstadoHomologacion.SOLICITADA
        )
        context["can_assign_evaluator"] = (
            is_superadmin(user)
            or (
                "coordinador" in roles
                and homologacion.programa_asignatura.programa_academico_id
                in coordinated_program_ids
            )
        ) and homologacion.estado_homologacion in {
            Homologacion.EstadoHomologacion.SOLICITADA,
            Homologacion.EstadoHomologacion.EN_REVISION,
        }
        context["can_evaluate_homologacion"] = (
            is_superadmin(user)
            or ("docente" in roles and professor == homologacion.profesor_evaluador)
        ) and homologacion.estado_homologacion in {
            Homologacion.EstadoHomologacion.SOLICITADA,
            Homologacion.EstadoHomologacion.EN_REVISION,
        }
        return context


class HomologacionCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    allowed_roles = ("estudiante", "superadmin")
    model = Homologacion
    form_class = HomologacionSolicitudForm
    template_name = "homologaciones/homologacion_form.html"
    success_url = reverse_lazy("homologaciones:homologacion_list")

    def dispatch(self, request, *args, **kwargs):
        if is_superadmin(request.user):
            messages.error(
                request,
                "La solicitud directa esta disponible para usuarios estudiantes.",
            )
            return redirect("homologaciones:homologacion_list")
        if not get_student_for_user(request.user):
            messages.error(
                request,
                "No tienes un registro de estudiante asociado para crear solicitudes.",
            )
            return redirect("homologaciones:homologacion_list")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            "Solicitud de homologacion creada correctamente.",
        )
        return super().form_valid(form)


class HomologacionAssignEvaluatorView(
    LoginRequiredMixin,
    RoleRequiredMixin,
    UpdateView,
):
    allowed_roles = ("coordinador", "superadmin")
    model = Homologacion
    form_class = HomologacionAsignarEvaluadorForm
    template_name = "homologaciones/homologacion_asignar_evaluador.html"
    pk_url_kwarg = "id_homologacion"

    def get_queryset(self):
        queryset = Homologacion.objects.select_related(
            "estudiante__usuario",
            "programa_asignatura__asignatura",
            "programa_asignatura__programa_academico",
            "profesor_evaluador__usuario",
        )
        if is_superadmin(self.request.user):
            return queryset
        return queryset.filter(
            programa_asignatura__programa_academico_id__in=get_coordinated_program_ids(
                self.request.user,
            ),
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy(
            "homologaciones:homologacion_detail",
            kwargs={"id_homologacion": self.object.id_homologacion},
        )

    def form_valid(self, form):
        messages.success(
            self.request,
            "Profesor evaluador asignado correctamente.",
        )
        return super().form_valid(form)


class HomologacionEvaluateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    allowed_roles = ("docente", "superadmin")
    model = Homologacion
    form_class = HomologacionEvaluarForm
    template_name = "homologaciones/homologacion_evaluar.html"
    pk_url_kwarg = "id_homologacion"

    def get_queryset(self):
        queryset = Homologacion.objects.select_related(
            "estudiante__usuario",
            "programa_asignatura__asignatura",
            "programa_asignatura__programa_academico",
            "profesor_evaluador__usuario",
        )
        if is_superadmin(self.request.user):
            return queryset
        professor = get_professor_for_user(self.request.user)
        if not professor:
            return queryset.none()
        return queryset.filter(profesor_evaluador=professor)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy(
            "homologaciones:homologacion_detail",
            kwargs={"id_homologacion": self.object.id_homologacion},
        )

    def form_valid(self, form):
        messages.success(self.request, "Homologacion evaluada correctamente.")
        return super().form_valid(form)


class HomologacionCancelView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = ("estudiante", "superadmin")

    def post(self, request, *args, **kwargs):
        queryset = filter_homologaciones_for_user(
            Homologacion.objects.all(),
            request.user,
        )
        homologacion = get_object_or_404(
            queryset,
            pk=kwargs["id_homologacion"],
        )

        student = get_student_for_user(request.user)
        if not is_superadmin(request.user) and homologacion.estudiante != student:
            messages.error(request, "Solo puedes cancelar tus propias solicitudes.")
            return redirect("homologaciones:homologacion_list")

        if (
            homologacion.estado_homologacion
            != Homologacion.EstadoHomologacion.SOLICITADA
        ):
            messages.error(
                request,
                "Solo se pueden cancelar solicitudes en estado Solicitada.",
            )
            return redirect(
                "homologaciones:homologacion_detail",
                id_homologacion=homologacion.id_homologacion,
            )

        homologacion.estado_homologacion = Homologacion.EstadoHomologacion.CANCELADA
        homologacion.save(update_fields=["estado_homologacion"])
        messages.success(request, "Solicitud de homologacion cancelada correctamente.")
        return redirect("homologaciones:homologacion_list")
