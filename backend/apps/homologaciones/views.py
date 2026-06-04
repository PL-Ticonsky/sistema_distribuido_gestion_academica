from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView

from apps.academica.distributed_write import cancel_homologacion
from apps.accounts.access import HOMOLOGATION_ROLES, RoleRequiredMixin
from apps.accounts.access_context import filter_homologaciones_for_user
from apps.accounts.roles import get_user_roles
from apps.auditoria.services import registrar_auditoria
from apps.homologaciones.forms import (
    HomologacionAssignEvaluatorForm,
    HomologacionEvaluateForm,
    HomologacionForm,
)
from apps.homologaciones.models import HomologacionGlobal
from apps.reportes.choices import (
    distinct_choices,
    estudiante_labels,
    facultad_choices,
    facultad_labels,
    profesor_labels,
    programa_asignatura_labels,
)

HOMOLOGATION_MANAGE_ROLES = ("coordinador", "decano", "superadmin")
HOMOLOGATION_EVALUATE_ROLES = ("docente", "coordinador", "decano", "superadmin")


def _has_role(user, roles):
    current_roles = set(get_user_roles(user))
    return "superadmin" in current_roles or bool(current_roles.intersection(roles))


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
        queryset = filter_homologaciones_for_user(
            super().get_queryset(),
            self.request.user,
        )
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
        context["can_create_homologaciones"] = True
        context["can_edit_homologaciones"] = _has_role(
            self.request.user,
            HOMOLOGATION_MANAGE_ROLES,
        )
        context["can_assign_homologaciones"] = _has_role(
            self.request.user,
            HOMOLOGATION_MANAGE_ROLES,
        )
        context["can_evaluate_homologaciones"] = _has_role(
            self.request.user,
            HOMOLOGATION_EVALUATE_ROLES,
        )
        context["can_cancel_homologaciones"] = _has_role(
            self.request.user,
            HOMOLOGATION_MANAGE_ROLES,
        )
        context["facultad_choices"] = facultad_choices()
        context["estado_choices"] = distinct_choices(
            HomologacionGlobal,
            "estado_homologacion",
            "Todos los estados",
        )
        estudiantes = estudiante_labels(
            [homologacion.id_estudiante for homologacion in context["homologaciones"]],
        )
        profesores = profesor_labels(
            [
                homologacion.id_profesor_evaluador
                for homologacion in context["homologaciones"]
            ],
        )
        facultades = facultad_labels(
            [homologacion.id_facultad for homologacion in context["homologaciones"]],
        )
        asignaturas_destino = programa_asignatura_labels(
            [
                homologacion.id_programa_asignatura
                for homologacion in context["homologaciones"]
            ],
        )
        for homologacion in context["homologaciones"]:
            homologacion.estudiante_label = estudiantes.get(
                homologacion.id_estudiante,
            )
            homologacion.profesor_label = profesores.get(
                homologacion.id_profesor_evaluador,
            )
            homologacion.facultad_label = facultades.get(homologacion.id_facultad)
            homologacion.asignatura_destino_label = asignaturas_destino.get(
                homologacion.id_programa_asignatura,
            )
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

    def get_queryset(self):
        return filter_homologaciones_for_user(
            super().get_queryset(),
            self.request.user,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_edit_homologaciones"] = _has_role(
            self.request.user,
            HOMOLOGATION_MANAGE_ROLES,
        )
        context["can_assign_homologaciones"] = _has_role(
            self.request.user,
            HOMOLOGATION_MANAGE_ROLES,
        )
        context["can_evaluate_homologaciones"] = _has_role(
            self.request.user,
            HOMOLOGATION_EVALUATE_ROLES,
        )
        context["can_cancel_homologaciones"] = _has_role(
            self.request.user,
            HOMOLOGATION_MANAGE_ROLES,
        )
        estudiantes = estudiante_labels([self.object.id_estudiante])
        profesores = profesor_labels([self.object.id_profesor_evaluador])
        facultades = facultad_labels([self.object.id_facultad])
        asignaturas_destino = programa_asignatura_labels(
            [self.object.id_programa_asignatura],
        )
        context["estudiante_label"] = estudiantes.get(self.object.id_estudiante)
        context["profesor_label"] = profesores.get(self.object.id_profesor_evaluador)
        context["facultad_label"] = facultades.get(self.object.id_facultad)
        context["asignatura_destino_label"] = asignaturas_destino.get(
            self.object.id_programa_asignatura,
        )
        return context


class HomologacionCreateView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    allowed_roles = HOMOLOGATION_ROLES
    form_class = HomologacionForm
    template_name = "homologaciones/homologacion_form.html"
    success_url = reverse_lazy("homologaciones:homologacion_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["selected_facultad"] = self.request.GET.get("id_facultad")
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        id_homologacion = form.save()
        registrar_auditoria(
            self.request.user,
            "CREAR_HOMOLOGACION",
            f"Homologacion creada: {id_homologacion}",
            esquema_afectado="fdw_*",
            tabla_afectada="homologacion",
        )
        messages.success(self.request, "Homologacion creada en el nodo distribuido.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Crear homologacion"
        context["submit_label"] = "Crear homologacion"
        context["facultad_choices"] = facultad_choices("Seleccione facultad")
        context["selected_facultad"] = self.request.GET.get("id_facultad", "")
        return context


class HomologacionUpdateView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    allowed_roles = HOMOLOGATION_MANAGE_ROLES
    form_class = HomologacionForm
    template_name = "homologaciones/homologacion_form.html"
    success_url = reverse_lazy("homologaciones:homologacion_list")

    def dispatch(self, request, *args, **kwargs):
        self.homologacion = get_object_or_404(
            filter_homologaciones_for_user(
                HomologacionGlobal.objects.all(),
                request.user,
            ),
            pk=kwargs["id_homologacion"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["homologacion"] = self.homologacion
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        updated_rows = form.save()
        if updated_rows:
            registrar_auditoria(
                self.request.user,
                "EDITAR_HOMOLOGACION",
                f"Homologacion actualizada: {self.homologacion.id_homologacion}",
                esquema_afectado="fdw_*",
                tabla_afectada="homologacion",
            )
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
    allowed_roles = HOMOLOGATION_MANAGE_ROLES
    form_class = HomologacionAssignEvaluatorForm
    template_name = "homologaciones/homologacion_asignar_evaluador.html"
    success_url = reverse_lazy("homologaciones:homologacion_list")

    def dispatch(self, request, *args, **kwargs):
        self.homologacion = get_object_or_404(
            filter_homologaciones_for_user(
                HomologacionGlobal.objects.all(),
                request.user,
            ),
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
            registrar_auditoria(
                self.request.user,
                "ASIGNAR_EVALUADOR_HOMOLOGACION",
                (
                    "Evaluador asignado a homologacion: "
                    f"{self.homologacion.id_homologacion}"
                ),
                esquema_afectado="fdw_*",
                tabla_afectada="homologacion",
            )
            messages.success(self.request, "Evaluador asignado.")
        else:
            messages.warning(self.request, "No se encontro la homologacion.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["homologacion"] = self.homologacion
        context["facultad_label"] = facultad_labels(
            [self.homologacion.id_facultad],
        ).get(self.homologacion.id_facultad)
        return context


class HomologacionEvaluateView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    allowed_roles = HOMOLOGATION_EVALUATE_ROLES
    form_class = HomologacionEvaluateForm
    template_name = "homologaciones/homologacion_evaluar.html"
    success_url = reverse_lazy("homologaciones:homologacion_list")

    def dispatch(self, request, *args, **kwargs):
        self.homologacion = get_object_or_404(
            filter_homologaciones_for_user(
                HomologacionGlobal.objects.all(),
                request.user,
            ),
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
            registrar_auditoria(
                self.request.user,
                "EVALUAR_HOMOLOGACION",
                f"Homologacion evaluada: {self.homologacion.id_homologacion}",
                esquema_afectado="fdw_*",
                tabla_afectada="homologacion",
            )
            messages.success(self.request, "Homologacion evaluada.")
        else:
            messages.warning(self.request, "No se encontro la homologacion.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["homologacion"] = self.homologacion
        context["facultad_label"] = facultad_labels(
            [self.homologacion.id_facultad],
        ).get(self.homologacion.id_facultad)
        return context


class HomologacionCancelView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = HOMOLOGATION_MANAGE_ROLES
    template_name = "homologaciones/homologacion_confirm_cancel.html"

    def dispatch(self, request, *args, **kwargs):
        self.homologacion = get_object_or_404(
            filter_homologaciones_for_user(
                HomologacionGlobal.objects.all(),
                request.user,
            ),
            pk=kwargs["id_homologacion"],
        )
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        updated_rows = cancel_homologacion(
            id_homologacion=self.homologacion.id_homologacion,
            id_facultad=self.homologacion.id_facultad,
        )
        if updated_rows:
            registrar_auditoria(
                request.user,
                "CANCELAR_HOMOLOGACION",
                f"Homologacion cancelada: {self.homologacion.id_homologacion}",
                esquema_afectado="fdw_*",
                tabla_afectada="homologacion",
            )
            messages.success(request, "Homologacion marcada como Cancelada.")
        else:
            messages.warning(request, "No se encontro la homologacion para cancelar.")
        return redirect("homologaciones:homologacion_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["homologacion"] = self.homologacion
        return context
