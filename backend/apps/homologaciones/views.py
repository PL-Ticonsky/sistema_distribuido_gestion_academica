from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView

from apps.academica.distributed_write import cancel_homologacion
from apps.accounts.access import HOMOLOGATION_ROLES, RoleRequiredMixin
from apps.homologaciones.forms import (
    HomologacionAssignEvaluatorForm,
    HomologacionEvaluateForm,
    HomologacionForm,
)
from apps.homologaciones.models import HomologacionGlobal


class HomologacionListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = HOMOLOGATION_ROLES
    model = HomologacionGlobal
    template_name = "homologaciones/homologacion_list.html"
    context_object_name = "homologaciones"
    paginate_by = 25
    filters = (
        "id_facultad",
        "estado_homologacion",
        "fecha_solicitud",
        "id_estudiante",
        "id_profesor_evaluador",
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        forced_state = getattr(self, "forced_state", None)
        if forced_state:
            queryset = queryset.filter(estado_homologacion=forced_state)
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
        context["can_write_homologaciones"] = True
        return context


class HomologacionSolicitudesListView(HomologacionListView):
    forced_state = "Solicitada"


class HomologacionPendientesListView(HomologacionListView):
    forced_state = "En revision"


class HomologacionDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    allowed_roles = HOMOLOGATION_ROLES
    model = HomologacionGlobal
    template_name = "homologaciones/homologacion_detail.html"
    context_object_name = "homologacion"
    pk_url_kwarg = "id_homologacion"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_write_homologaciones"] = True
        return context


class HomologacionCreateView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    allowed_roles = HOMOLOGATION_ROLES
    form_class = HomologacionForm
    template_name = "homologaciones/homologacion_form.html"
    success_url = reverse_lazy("homologaciones:homologacion_list")

    def form_valid(self, form):
        form.save()
        # TODO: registrar auditoria distribuida cuando se consolide el contrato.
        messages.success(self.request, "Homologacion creada en el nodo distribuido.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Crear homologacion"
        context["submit_label"] = "Crear homologacion"
        return context


class HomologacionUpdateView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    allowed_roles = HOMOLOGATION_ROLES
    form_class = HomologacionForm
    template_name = "homologaciones/homologacion_form.html"
    success_url = reverse_lazy("homologaciones:homologacion_list")

    def dispatch(self, request, *args, **kwargs):
        self.homologacion = get_object_or_404(
            HomologacionGlobal,
            pk=kwargs["id_homologacion"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["homologacion"] = self.homologacion
        return kwargs

    def form_valid(self, form):
        updated_rows = form.save()
        if updated_rows:
            messages.success(
                self.request,
                "Homologacion actualizada en el nodo distribuido.",
            )
        else:
            messages.warning(
                self.request,
                "No se encontro la homologacion para actualizar.",
            )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["homologacion"] = self.homologacion
        context["form_title"] = "Editar homologacion"
        context["submit_label"] = "Guardar cambios"
        return context


class HomologacionAssignEvaluatorView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    allowed_roles = HOMOLOGATION_ROLES
    form_class = HomologacionAssignEvaluatorForm
    template_name = "homologaciones/homologacion_asignar_evaluador.html"
    success_url = reverse_lazy("homologaciones:homologacion_list")

    def dispatch(self, request, *args, **kwargs):
        self.homologacion = get_object_or_404(
            HomologacionGlobal,
            pk=kwargs["id_homologacion"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["homologacion"] = self.homologacion
        return kwargs

    def form_valid(self, form):
        updated_rows = form.save()
        if updated_rows:
            messages.success(self.request, "Evaluador asignado.")
        else:
            messages.warning(self.request, "No se encontro la homologacion.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["homologacion"] = self.homologacion
        return context


class HomologacionEvaluateView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    allowed_roles = HOMOLOGATION_ROLES
    form_class = HomologacionEvaluateForm
    template_name = "homologaciones/homologacion_evaluar.html"
    success_url = reverse_lazy("homologaciones:homologacion_list")

    def dispatch(self, request, *args, **kwargs):
        self.homologacion = get_object_or_404(
            HomologacionGlobal,
            pk=kwargs["id_homologacion"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["homologacion"] = self.homologacion
        return kwargs

    def form_valid(self, form):
        updated_rows = form.save()
        if updated_rows:
            messages.success(self.request, "Homologacion evaluada.")
        else:
            messages.warning(self.request, "No se encontro la homologacion.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["homologacion"] = self.homologacion
        return context


class HomologacionCancelView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = HOMOLOGATION_ROLES
    template_name = "homologaciones/homologacion_confirm_cancel.html"

    def dispatch(self, request, *args, **kwargs):
        self.homologacion = get_object_or_404(
            HomologacionGlobal,
            pk=kwargs["id_homologacion"],
        )
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        updated_rows = cancel_homologacion(
            id_homologacion=self.homologacion.id_homologacion,
            id_facultad=self.homologacion.id_facultad,
        )
        if updated_rows:
            messages.success(request, "Homologacion marcada como Cancelada.")
        else:
            messages.warning(request, "No se encontro la homologacion para cancelar.")
        return redirect("homologaciones:homologacion_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["homologacion"] = self.homologacion
        return context
