from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.accounts.access import FINANCIAL_ROLES, RoleRequiredMixin
from apps.accounts.scope import (
    get_visible_student_ids,
    is_superadmin,
)
from apps.financiera.forms import (
    MatriculaCreateForm,
    ReciboForm,
    TarifaMatriculaForm,
    get_financial_program_ids,
    user_can_manage_financial,
    validate_matricula_limit,
)
from apps.financiera.models import Matricula, Recibo, TarifaMatricula


def filter_financial_queryset_for_user(queryset, user, *, path_prefix=""):
    if is_superadmin(user):
        return queryset

    student_ids = get_visible_student_ids(user)
    if not student_ids:
        return queryset.none()
    return queryset.filter(
        **{f"{path_prefix}estudiante_id__in": student_ids},
    ).distinct()


def filter_tarifas_for_user(queryset, user):
    if is_superadmin(user):
        return queryset

    program_ids = get_financial_program_ids(user)
    if not program_ids:
        return queryset.none()
    return queryset.filter(programa_academico_id__in=program_ids).distinct()


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
        return filter_tarifas_for_user(queryset, self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage_financial"] = user_can_manage_financial(self.request.user)
        return context


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage_financial"] = user_can_manage_financial(self.request.user)
        return context


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage_financial"] = user_can_manage_financial(self.request.user)
        return context


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage_financial"] = user_can_manage_financial(self.request.user)
        return context


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage_financial"] = user_can_manage_financial(self.request.user)
        return context


class FinancialManageMixin(LoginRequiredMixin, RoleRequiredMixin):
    allowed_roles = ("administrativo", "superadmin")

    def dispatch(self, request, *args, **kwargs):
        if not user_can_manage_financial(request.user):
            messages.error(
                request,
                "No tienes permisos para modificar datos financieros.",
            )
            return redirect("accounts:dashboard")
        return super().dispatch(request, *args, **kwargs)


class TarifaMatriculaCreateView(FinancialManageMixin, CreateView):
    model = TarifaMatricula
    form_class = TarifaMatriculaForm
    template_name = "financiera/tarifa_form.html"
    success_url = reverse_lazy("financiera:tarifa_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Tarifa creada correctamente.")
        return super().form_valid(form)


class TarifaMatriculaUpdateView(FinancialManageMixin, UpdateView):
    model = TarifaMatricula
    form_class = TarifaMatriculaForm
    template_name = "financiera/tarifa_form.html"
    pk_url_kwarg = "id_tarifa_matricula"
    success_url = reverse_lazy("financiera:tarifa_list")

    def get_queryset(self):
        return filter_tarifas_for_user(TarifaMatricula.objects.all(), self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Tarifa actualizada correctamente.")
        return super().form_valid(form)


class TarifaMatriculaToggleEstadoView(FinancialManageMixin, View):
    def post(self, request, *args, **kwargs):
        tarifa = get_object_or_404(
            filter_tarifas_for_user(TarifaMatricula.objects.all(), request.user),
            pk=kwargs["id_tarifa_matricula"],
        )
        tarifa.estado = (
            TarifaMatricula.Estado.INACTIVA
            if tarifa.estado == TarifaMatricula.Estado.ACTIVA
            else TarifaMatricula.Estado.ACTIVA
        )
        tarifa.save(update_fields=["estado"])
        messages.success(request, "Estado de tarifa actualizado correctamente.")
        return redirect("financiera:tarifa_list")


class ReciboCreateView(FinancialManageMixin, CreateView):
    model = Recibo
    form_class = ReciboForm
    template_name = "financiera/recibo_form.html"
    success_url = reverse_lazy("financiera:recibo_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Recibo creado correctamente.")
        return super().form_valid(form)


class ReciboUpdateView(FinancialManageMixin, UpdateView):
    model = Recibo
    form_class = ReciboForm
    template_name = "financiera/recibo_form.html"
    pk_url_kwarg = "id_recibo"

    def get_queryset(self):
        return filter_financial_queryset_for_user(
            Recibo.objects.select_related("estudiante", "tarifa_matricula"),
            self.request.user,
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy(
            "financiera:recibo_detail",
            kwargs={"id_recibo": self.object.id_recibo},
        )

    def form_valid(self, form):
        messages.success(self.request, "Recibo actualizado correctamente.")
        return super().form_valid(form)


class ReciboAnularView(FinancialManageMixin, View):
    def post(self, request, *args, **kwargs):
        recibo = get_object_or_404(
            filter_financial_queryset_for_user(Recibo.objects.all(), request.user),
            pk=kwargs["id_recibo"],
        )
        if recibo.estado_pago == Recibo.EstadoPago.ANULADO:
            messages.error(request, "El recibo ya se encuentra anulado.")
        else:
            recibo.estado_pago = Recibo.EstadoPago.ANULADO
            recibo.fecha_pago = None
            recibo.valor_pagado = None
            recibo.metodo_pago = None
            recibo.save(
                update_fields=[
                    "estado_pago",
                    "fecha_pago",
                    "valor_pagado",
                    "metodo_pago",
                ],
            )
            messages.success(request, "Recibo anulado correctamente.")
        return redirect("financiera:recibo_detail", id_recibo=recibo.id_recibo)


class MatriculaCreateView(FinancialManageMixin, CreateView):
    model = Matricula
    form_class = MatriculaCreateForm
    template_name = "financiera/matricula_form.html"
    success_url = reverse_lazy("financiera:matricula_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Matricula creada correctamente.")
        return super().form_valid(form)


class MatriculaEstadoView(FinancialManageMixin, View):
    target_state = None
    success_message = "Estado de matricula actualizado correctamente."

    def post(self, request, *args, **kwargs):
        matricula = get_object_or_404(
            filter_financial_queryset_for_user(
                Matricula.objects.select_related("recibo__estudiante"),
                request.user,
                path_prefix="recibo__",
            ),
            pk=kwargs["id_matricula"],
        )

        if matricula.estado_matricula == Matricula.EstadoMatricula.ANULADA:
            messages.error(request, "No se puede modificar una matricula anulada.")
            return redirect(
                "financiera:matricula_detail",
                id_matricula=matricula.id_matricula,
            )

        if (
            matricula.estado_matricula == Matricula.EstadoMatricula.CANCELADA
            and self.target_state == Matricula.EstadoMatricula.ACTIVA
        ):
            messages.error(request, "No se puede activar una matricula cancelada.")
            return redirect(
                "financiera:matricula_detail",
                id_matricula=matricula.id_matricula,
            )

        if self.target_state == Matricula.EstadoMatricula.ACTIVA:
            if matricula.recibo.estado_pago != Recibo.EstadoPago.PAGADO:
                messages.error(request, "No se puede activar con recibo no pagado.")
                return redirect(
                    "financiera:matricula_detail",
                    id_matricula=matricula.id_matricula,
                )
            try:
                validate_matricula_limit(matricula.recibo.estudiante)
            except ValidationError as error:
                messages.error(request, str(error))
                return redirect(
                    "financiera:matricula_detail",
                    id_matricula=matricula.id_matricula,
                )

        matricula.estado_matricula = self.target_state
        matricula.save(update_fields=["estado_matricula"])
        messages.success(request, self.success_message)
        return redirect(
            "financiera:matricula_detail",
            id_matricula=matricula.id_matricula,
        )


class MatriculaActivarView(MatriculaEstadoView):
    target_state = Matricula.EstadoMatricula.ACTIVA
    success_message = "Matricula activada correctamente."


class MatriculaFinalizarView(MatriculaEstadoView):
    target_state = Matricula.EstadoMatricula.FINALIZADA
    success_message = "Matricula finalizada correctamente."


class MatriculaCancelarView(MatriculaEstadoView):
    target_state = Matricula.EstadoMatricula.CANCELADA
    success_message = "Matricula cancelada correctamente."


class MatriculaAnularView(MatriculaEstadoView):
    target_state = Matricula.EstadoMatricula.ANULADA
    success_message = "Matricula anulada correctamente."
