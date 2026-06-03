from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView

from apps.accounts.access import FINANCIAL_ROLES, RoleRequiredMixin
from apps.auditoria.services import registrar_auditoria
from apps.financiera.forms import (
    MatriculaForm,
    ReciboForm,
    TarifaMatriculaForm,
    anular_recibo_from_instance,
    cancel_matricula_from_instance,
    deactivate_tarifa_from_instance,
    user_can_manage_financial,
)
from apps.financiera.models import MatriculaDetalle, Recibo, TarifaMatricula


class FinancialReadOnlyListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = FINANCIAL_ROLES
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
        context["can_manage_financial"] = user_can_manage_financial(self.request.user)
        return context


class FinancialManageMixin(LoginRequiredMixin, RoleRequiredMixin):
    allowed_roles = FINANCIAL_ROLES

    def dispatch(self, request, *args, **kwargs):
        if not user_can_manage_financial(request.user):
            messages.error(request, "No tienes permisos para modificar financiera.")
            return redirect("financiera:tarifa_list")
        return super().dispatch(request, *args, **kwargs)


class TarifaMatriculaListView(FinancialReadOnlyListView):
    model = TarifaMatricula
    template_name = "financiera/tarifa_list.html"
    context_object_name = "tarifas"
    filters = ("id_facultad", "programa_academico_id", "periodo_academico_id", "estado")

    def get_queryset(self):
        return super().get_queryset().select_related(
            "programa_academico",
            "programa_academico__facultad",
            "periodo_academico",
        )


class TarifaMatriculaDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    allowed_roles = FINANCIAL_ROLES
    model = TarifaMatricula
    template_name = "financiera/tarifa_detail.html"
    context_object_name = "tarifa"
    pk_url_kwarg = "id_tarifa_matricula"

    def get_queryset(self):
        return super().get_queryset().select_related(
            "programa_academico",
            "programa_academico__facultad",
            "periodo_academico",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage_financial"] = user_can_manage_financial(self.request.user)
        return context


class TarifaMatriculaCreateView(FinancialManageMixin, FormView):
    form_class = TarifaMatriculaForm
    template_name = "financiera/tarifa_form.html"
    success_url = reverse_lazy("financiera:tarifa_list")

    def form_valid(self, form):
        id_tarifa = form.save()
        registrar_auditoria(
            self.request.user,
            "CREAR_TARIFA",
            f"Tarifa creada: {id_tarifa}",
            esquema_afectado="financiero",
            tabla_afectada="tarifa_matricula",
        )
        messages.success(self.request, "Tarifa creada en financiero.tarifa_matricula.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Crear tarifa de matricula"
        context["submit_label"] = "Crear tarifa"
        return context


class TarifaMatriculaUpdateView(FinancialManageMixin, FormView):
    form_class = TarifaMatriculaForm
    template_name = "financiera/tarifa_form.html"
    success_url = reverse_lazy("financiera:tarifa_list")

    def dispatch(self, request, *args, **kwargs):
        self.tarifa = get_object_or_404(
            TarifaMatricula,
            pk=kwargs["id_tarifa_matricula"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tarifa"] = self.tarifa
        return kwargs

    def form_valid(self, form):
        updated_rows = form.save()
        if updated_rows:
            registrar_auditoria(
                self.request.user,
                "EDITAR_TARIFA",
                f"Tarifa actualizada: {self.tarifa.id_tarifa_matricula}",
                esquema_afectado="financiero",
                tabla_afectada="tarifa_matricula",
            )
            messages.success(self.request, "Tarifa actualizada.")
        else:
            messages.warning(self.request, "No se encontro la tarifa.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tarifa"] = self.tarifa
        context["form_title"] = "Editar tarifa de matricula"
        context["submit_label"] = "Guardar tarifa"
        return context


class TarifaMatriculaDeactivateView(FinancialManageMixin, TemplateView):
    template_name = "financiera/tarifa_confirm_deactivate.html"

    def dispatch(self, request, *args, **kwargs):
        self.tarifa = get_object_or_404(
            TarifaMatricula,
            pk=kwargs["id_tarifa_matricula"],
        )
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        updated_rows = deactivate_tarifa_from_instance(self.tarifa)
        if updated_rows:
            registrar_auditoria(
                request.user,
                "DESACTIVAR_TARIFA",
                f"Tarifa desactivada: {self.tarifa.id_tarifa_matricula}",
                esquema_afectado="financiero",
                tabla_afectada="tarifa_matricula",
            )
            messages.success(request, "Tarifa marcada como Inactiva.")
        else:
            messages.warning(request, "No se encontro la tarifa.")
        return redirect("financiera:tarifa_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tarifa"] = self.tarifa
        return context


class ReciboListView(FinancialReadOnlyListView):
    model = Recibo
    template_name = "financiera/recibo_list.html"
    context_object_name = "recibos"
    filters = ("id_facultad", "tarifa_matricula__periodo_academico_id", "estado_pago")

    def get_queryset(self):
        return super().get_queryset().select_related(
            "tarifa_matricula",
            "tarifa_matricula__programa_academico",
            "tarifa_matricula__periodo_academico",
        )


class ReciboDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    allowed_roles = FINANCIAL_ROLES
    model = Recibo
    template_name = "financiera/recibo_detail.html"
    context_object_name = "recibo"
    pk_url_kwarg = "id_recibo"

    def get_queryset(self):
        return super().get_queryset().select_related(
            "tarifa_matricula",
            "tarifa_matricula__programa_academico",
            "tarifa_matricula__periodo_academico",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage_financial"] = user_can_manage_financial(self.request.user)
        return context


class ReciboCreateView(FinancialManageMixin, FormView):
    form_class = ReciboForm
    template_name = "financiera/recibo_form.html"
    success_url = reverse_lazy("financiera:recibo_list")

    def form_valid(self, form):
        id_recibo = form.save()
        registrar_auditoria(
            self.request.user,
            "CREAR_RECIBO",
            f"Recibo creado: {id_recibo}",
            esquema_afectado="financiero",
            tabla_afectada="recibo",
        )
        messages.success(self.request, "Recibo creado en financiero.recibo.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Crear recibo"
        context["submit_label"] = "Crear recibo"
        return context


class ReciboUpdateView(FinancialManageMixin, FormView):
    form_class = ReciboForm
    template_name = "financiera/recibo_form.html"
    success_url = reverse_lazy("financiera:recibo_list")

    def dispatch(self, request, *args, **kwargs):
        self.recibo = get_object_or_404(Recibo, pk=kwargs["id_recibo"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["recibo"] = self.recibo
        return kwargs

    def form_valid(self, form):
        updated_rows = form.save()
        if updated_rows:
            registrar_auditoria(
                self.request.user,
                "EDITAR_RECIBO",
                f"Recibo actualizado: {self.recibo.id_recibo}",
                esquema_afectado="financiero",
                tabla_afectada="recibo",
            )
            messages.success(self.request, "Recibo actualizado.")
        else:
            messages.warning(self.request, "No se encontro el recibo.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recibo"] = self.recibo
        context["form_title"] = "Editar recibo"
        context["submit_label"] = "Guardar recibo"
        return context


class ReciboAnularView(FinancialManageMixin, TemplateView):
    template_name = "financiera/recibo_confirm_anular.html"

    def dispatch(self, request, *args, **kwargs):
        self.recibo = get_object_or_404(Recibo, pk=kwargs["id_recibo"])
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        updated_rows = anular_recibo_from_instance(self.recibo)
        if updated_rows:
            registrar_auditoria(
                request.user,
                "ANULAR_RECIBO",
                f"Recibo anulado: {self.recibo.id_recibo}",
                esquema_afectado="financiero",
                tabla_afectada="recibo",
            )
            messages.success(request, "Recibo marcado como Anulado.")
        else:
            messages.warning(request, "No se encontro el recibo.")
        return redirect("financiera:recibo_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recibo"] = self.recibo
        return context


class MatriculaListView(FinancialReadOnlyListView):
    model = MatriculaDetalle
    template_name = "financiera/matricula_list.html"
    context_object_name = "matriculas"
    filters = (
        "id_facultad",
        "nombre_facultad",
        "id_programa_academico",
        "nombre_programa",
        "id_periodo_academico",
        "estado_pago",
        "estado_matricula",
    )


class MatriculaDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    allowed_roles = FINANCIAL_ROLES
    model = MatriculaDetalle
    template_name = "financiera/matricula_detail.html"
    context_object_name = "matricula"
    pk_url_kwarg = "id_matricula"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage_financial"] = user_can_manage_financial(self.request.user)
        return context


class MatriculaCreateView(FinancialManageMixin, FormView):
    form_class = MatriculaForm
    template_name = "financiera/matricula_form.html"
    success_url = reverse_lazy("financiera:matricula_list")

    def form_valid(self, form):
        id_matricula = form.save()
        registrar_auditoria(
            self.request.user,
            "CREAR_MATRICULA",
            f"Matricula creada: {id_matricula}",
            esquema_afectado="fdw_*",
            tabla_afectada="matricula",
        )
        messages.success(self.request, "Matricula creada en el nodo distribuido.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Crear matricula"
        context["submit_label"] = "Crear matricula"
        return context


class MatriculaUpdateView(FinancialManageMixin, FormView):
    form_class = MatriculaForm
    template_name = "financiera/matricula_form.html"
    success_url = reverse_lazy("financiera:matricula_list")

    def dispatch(self, request, *args, **kwargs):
        self.matricula = get_object_or_404(
            MatriculaDetalle,
            pk=kwargs["id_matricula"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["matricula"] = self.matricula
        return kwargs

    def form_valid(self, form):
        updated_rows = form.save()
        if updated_rows:
            registrar_auditoria(
                self.request.user,
                "EDITAR_MATRICULA",
                f"Matricula actualizada: {self.matricula.id_matricula}",
                esquema_afectado="fdw_*",
                tabla_afectada="matricula",
            )
            messages.success(self.request, "Matricula actualizada.")
        else:
            messages.warning(self.request, "No se encontro la matricula.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["matricula"] = self.matricula
        context["form_title"] = "Editar matricula"
        context["submit_label"] = "Guardar matricula"
        return context


class MatriculaCancelarView(FinancialManageMixin, TemplateView):
    template_name = "financiera/matricula_confirm_cancel.html"

    def dispatch(self, request, *args, **kwargs):
        self.matricula = get_object_or_404(
            MatriculaDetalle,
            pk=kwargs["id_matricula"],
        )
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        updated_rows = cancel_matricula_from_instance(self.matricula)
        if updated_rows:
            registrar_auditoria(
                request.user,
                "CANCELAR_MATRICULA",
                f"Matricula cancelada: {self.matricula.id_matricula}",
                esquema_afectado="fdw_*",
                tabla_afectada="matricula",
            )
            messages.success(request, "Matricula marcada como Cancelada.")
        else:
            messages.warning(request, "No se encontro la matricula.")
        return redirect("financiera:matricula_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["matricula"] = self.matricula
        return context
