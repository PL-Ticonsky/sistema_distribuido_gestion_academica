from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView, View

from apps.academica.distributed_write import (
    cancel_inscripcion,
    deactivate_or_cancel_grupo,
    delete_or_deactivate_estudiante,
)
from apps.academica.forms import (
    EstudianteCreateForm,
    EstudianteUpdateForm,
    GrupoCreateForm,
    GrupoUpdateForm,
    InscripcionCreateForm,
    InscripcionUpdateForm,
    user_can_create_groups,
    user_can_create_students,
    user_can_write_enrollments,
)
from apps.accounts.access import (
    STUDENT_ROLES,
    TEACHING_ROLES,
    RoleRequiredMixin,
)
from apps.auditoria.services import registrar_auditoria
from apps.estructura.models import Asignatura
from apps.reportes.choices import (
    distinct_choices,
    facultad_choices,
    periodo_choices,
    programa_choices,
)
from apps.reportes.models import (
    EstudianteDetalle,
    GrupoDetalle,
    InscripcionDetalle,
    ProfesorDetalle,
)

ACADEMIC_READ_ROLES = (*STUDENT_ROLES, "docente")
STUDENT_WRITE_ROLES = ("coordinador", "superadmin")
GROUP_WRITE_ROLES = ("coordinador", "superadmin")
ENROLLMENT_WRITE_ROLES = ("estudiante", "coordinador", "decano", "superadmin")
READ_ONLY_MESSAGE = "La escritura academica distribuida aun no esta habilitada."


class AcademicReportListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
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
        return context


class AsignaturaListView(AcademicReportListView):
    allowed_roles = ACADEMIC_READ_ROLES
    model = Asignatura
    template_name = "academica/asignatura_list.html"
    context_object_name = "asignaturas"
    filters = ("estado",)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["estado_choices"] = distinct_choices(Asignatura, "estado", "Todos")
        return context


class EstudianteListView(AcademicReportListView):
    allowed_roles = STUDENT_ROLES
    model = EstudianteDetalle
    template_name = "academica/estudiante_list.html"
    context_object_name = "estudiantes"
    filters = (
        "id_facultad",
        "id_programa_academico",
        "estado_estudiante",
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_create_students"] = user_can_create_students(self.request.user)
        context["facultad_choices"] = facultad_choices()
        context["programa_choices"] = programa_choices(
            self.request.GET.get("id_facultad"),
        )
        context["estado_choices"] = distinct_choices(
            EstudianteDetalle,
            "estado_estudiante",
            "Todos los estados",
        )
        return context


class EstudianteDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    allowed_roles = STUDENT_ROLES
    model = EstudianteDetalle
    template_name = "academica/estudiante_detail.html"
    context_object_name = "estudiante"
    pk_url_kwarg = "id_estudiante"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_create_students"] = user_can_create_students(self.request.user)
        return context


class EstudianteCreateView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    allowed_roles = STUDENT_WRITE_ROLES
    form_class = EstudianteCreateForm
    template_name = "academica/estudiante_form.html"
    success_url = reverse_lazy("academica:estudiante_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["selected_facultad"] = self.request.GET.get("id_facultad")
        return kwargs

    def form_valid(self, form):
        id_estudiante = form.save()
        registrar_auditoria(
            self.request.user,
            "CREAR_ESTUDIANTE",
            f"Estudiante creado: {id_estudiante}",
            esquema_afectado="fdw_*",
            tabla_afectada="estudiante",
        )
        messages.success(self.request, "Estudiante creado en el nodo distribuido.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Crear estudiante"
        context["submit_label"] = "Crear estudiante"
        context["facultad_choices"] = facultad_choices("Seleccione facultad")
        context["selected_facultad"] = self.request.GET.get("id_facultad", "")
        return context


class EstudianteUpdateView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    allowed_roles = STUDENT_WRITE_ROLES
    form_class = EstudianteUpdateForm
    template_name = "academica/estudiante_form.html"
    success_url = reverse_lazy("academica:estudiante_list")

    def dispatch(self, request, *args, **kwargs):
        self.estudiante = get_object_or_404(
            EstudianteDetalle,
            pk=kwargs["id_estudiante"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["estudiante"] = self.estudiante
        kwargs["selected_facultad"] = self.estudiante.id_facultad
        return kwargs

    def form_valid(self, form):
        updated_rows = form.save()
        if updated_rows:
            registrar_auditoria(
                self.request.user,
                "EDITAR_ESTUDIANTE",
                f"Estudiante actualizado: {self.estudiante.id_estudiante}",
                esquema_afectado="fdw_*",
                tabla_afectada="estudiante",
            )
            messages.success(
                self.request,
                "Estudiante actualizado en el nodo distribuido.",
            )
        else:
            messages.warning(
                self.request,
                "No se encontro el estudiante para actualizar.",
            )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["estudiante"] = self.estudiante
        context["form_title"] = "Editar estudiante"
        context["submit_label"] = "Guardar cambios"
        return context


class EstudianteDeactivateView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = STUDENT_WRITE_ROLES
    template_name = "academica/estudiante_confirm_deactivate.html"

    def dispatch(self, request, *args, **kwargs):
        self.estudiante = get_object_or_404(
            EstudianteDetalle,
            pk=kwargs["id_estudiante"],
        )
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        updated_rows = delete_or_deactivate_estudiante(
            id_estudiante=self.estudiante.id_estudiante,
            id_facultad=self.estudiante.id_facultad,
        )
        if updated_rows:
            registrar_auditoria(
                request.user,
                "DESACTIVAR_ESTUDIANTE",
                f"Estudiante desactivado: {self.estudiante.id_estudiante}",
                esquema_afectado="fdw_*",
                tabla_afectada="estudiante",
            )
            messages.success(request, "Estudiante marcado como Inactivo.")
        else:
            messages.warning(request, "No se encontro el estudiante para desactivar.")
        return redirect("academica:estudiante_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["estudiante"] = self.estudiante
        return context


class ProfesorListView(AcademicReportListView):
    allowed_roles = TEACHING_ROLES
    model = ProfesorDetalle
    template_name = "academica/profesor_list.html"
    context_object_name = "profesores"
    filters = ("id_facultad", "categoria", "vinculacion")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["facultad_choices"] = facultad_choices()
        context["categoria_choices"] = distinct_choices(
            ProfesorDetalle,
            "categoria",
            "Todas las categorias",
        )
        context["vinculacion_choices"] = distinct_choices(
            ProfesorDetalle,
            "vinculacion",
            "Todas las vinculaciones",
        )
        return context


class GrupoListView(AcademicReportListView):
    allowed_roles = TEACHING_ROLES
    model = GrupoDetalle
    template_name = "academica/grupo_list.html"
    context_object_name = "grupos"
    filters = (
        "id_facultad",
        "id_programa_academico",
        "id_periodo_academico",
        "estado_grupo",
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_create_groups"] = user_can_create_groups(self.request.user)
        context["facultad_choices"] = facultad_choices()
        context["programa_choices"] = programa_choices(
            self.request.GET.get("id_facultad"),
        )
        context["periodo_choices"] = periodo_choices()
        context["estado_choices"] = distinct_choices(
            GrupoDetalle,
            "estado_grupo",
            "Todos los estados",
        )
        return context


class GrupoDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    allowed_roles = TEACHING_ROLES
    model = GrupoDetalle
    template_name = "academica/grupo_detail.html"
    context_object_name = "grupo"
    pk_url_kwarg = "id_grupo"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_create_groups"] = user_can_create_groups(self.request.user)
        return context


class GrupoCreateView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    allowed_roles = GROUP_WRITE_ROLES
    form_class = GrupoCreateForm
    template_name = "academica/grupo_form.html"
    success_url = reverse_lazy("academica:grupo_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["selected_facultad"] = self.request.GET.get("id_facultad")
        return kwargs

    def form_valid(self, form):
        id_grupo = form.save()
        registrar_auditoria(
            self.request.user,
            "CREAR_GRUPO",
            f"Grupo creado: {id_grupo}",
            esquema_afectado="fdw_*",
            tabla_afectada="grupo",
        )
        messages.success(self.request, "Grupo creado en el nodo distribuido.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Crear grupo"
        context["submit_label"] = "Crear grupo"
        context["facultad_choices"] = facultad_choices("Seleccione facultad")
        context["selected_facultad"] = self.request.GET.get("id_facultad", "")
        return context


class GrupoUpdateView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    allowed_roles = GROUP_WRITE_ROLES
    form_class = GrupoUpdateForm
    template_name = "academica/grupo_form.html"
    success_url = reverse_lazy("academica:grupo_list")

    def dispatch(self, request, *args, **kwargs):
        self.grupo = get_object_or_404(GrupoDetalle, pk=kwargs["id_grupo"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["grupo"] = self.grupo
        kwargs["selected_facultad"] = self.grupo.id_facultad
        return kwargs

    def form_valid(self, form):
        updated_rows = form.save()
        if updated_rows:
            registrar_auditoria(
                self.request.user,
                "EDITAR_GRUPO",
                f"Grupo actualizado: {self.grupo.id_grupo}",
                esquema_afectado="fdw_*",
                tabla_afectada="grupo",
            )
            messages.success(self.request, "Grupo actualizado en el nodo distribuido.")
        else:
            messages.warning(self.request, "No se encontro el grupo para actualizar.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["grupo"] = self.grupo
        context["form_title"] = "Editar grupo"
        context["submit_label"] = "Guardar cambios"
        return context


class GrupoCancelView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = GROUP_WRITE_ROLES
    template_name = "academica/grupo_confirm_cancel.html"

    def dispatch(self, request, *args, **kwargs):
        self.grupo = get_object_or_404(GrupoDetalle, pk=kwargs["id_grupo"])
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        updated_rows = deactivate_or_cancel_grupo(
            id_grupo=self.grupo.id_grupo,
            id_facultad=self.grupo.id_facultad,
        )
        if updated_rows:
            registrar_auditoria(
                request.user,
                "CANCELAR_GRUPO",
                f"Grupo cancelado: {self.grupo.id_grupo}",
                esquema_afectado="fdw_*",
                tabla_afectada="grupo",
            )
            messages.success(request, "Grupo marcado como Cancelado.")
        else:
            messages.warning(request, "No se encontro el grupo para cancelar.")
        return redirect("academica:grupo_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["grupo"] = self.grupo
        return context


class InscripcionListView(AcademicReportListView):
    allowed_roles = ACADEMIC_READ_ROLES
    model = InscripcionDetalle
    template_name = "academica/inscripcion_list.html"
    context_object_name = "inscripciones"
    filters = (
        "id_facultad",
        "id_programa_academico",
        "id_periodo_academico",
        "estado_inscripcion",
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_write_enrollments"] = user_can_write_enrollments(
            self.request.user,
        )
        context["facultad_choices"] = facultad_choices()
        context["programa_choices"] = programa_choices(
            self.request.GET.get("id_facultad"),
        )
        context["periodo_choices"] = periodo_choices()
        context["estado_choices"] = distinct_choices(
            InscripcionDetalle,
            "estado_inscripcion",
            "Todos los estados",
        )
        return context


class InscripcionDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    allowed_roles = ACADEMIC_READ_ROLES
    model = InscripcionDetalle
    template_name = "academica/inscripcion_detail.html"
    context_object_name = "inscripcion"
    pk_url_kwarg = "id_inscripcion"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_write_enrollments"] = user_can_write_enrollments(
            self.request.user,
        )
        return context


class InscripcionCreateView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    allowed_roles = ENROLLMENT_WRITE_ROLES
    form_class = InscripcionCreateForm
    template_name = "academica/inscripcion_form.html"
    success_url = reverse_lazy("academica:inscripcion_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["selected_facultad"] = self.request.GET.get("id_facultad")
        kwargs["selected_periodo"] = self.request.GET.get("id_periodo_academico")
        return kwargs

    def form_valid(self, form):
        id_inscripcion = form.save()
        registrar_auditoria(
            self.request.user,
            "CREAR_INSCRIPCION",
            f"Inscripcion creada: {id_inscripcion}",
            esquema_afectado="fdw_*",
            tabla_afectada="inscripcion",
        )
        messages.success(self.request, "Inscripcion creada en el nodo distribuido.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Crear inscripcion"
        context["submit_label"] = "Crear inscripcion"
        context["facultad_choices"] = facultad_choices("Seleccione facultad")
        context["periodo_choices"] = periodo_choices("Seleccione periodo")
        context["selected_facultad"] = self.request.GET.get("id_facultad", "")
        context["selected_periodo"] = self.request.GET.get(
            "id_periodo_academico",
            "",
        )
        return context


class InscripcionUpdateView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    allowed_roles = ENROLLMENT_WRITE_ROLES
    form_class = InscripcionUpdateForm
    template_name = "academica/inscripcion_form.html"
    success_url = reverse_lazy("academica:inscripcion_list")

    def dispatch(self, request, *args, **kwargs):
        self.inscripcion = get_object_or_404(
            InscripcionDetalle,
            pk=kwargs["id_inscripcion"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["inscripcion"] = self.inscripcion
        kwargs["selected_facultad"] = self.inscripcion.id_facultad
        kwargs["selected_periodo"] = self.inscripcion.id_periodo_academico
        return kwargs

    def form_valid(self, form):
        updated_rows = form.save()
        if updated_rows:
            registrar_auditoria(
                self.request.user,
                "EDITAR_INSCRIPCION",
                f"Inscripcion actualizada: {self.inscripcion.id_inscripcion}",
                esquema_afectado="fdw_*",
                tabla_afectada="inscripcion",
            )
            messages.success(
                self.request,
                "Inscripcion actualizada en el nodo distribuido.",
            )
        else:
            messages.warning(
                self.request,
                "No se encontro la inscripcion para actualizar.",
            )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["inscripcion"] = self.inscripcion
        context["form_title"] = "Editar inscripcion"
        context["submit_label"] = "Guardar cambios"
        return context


class InscripcionCancelView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = ENROLLMENT_WRITE_ROLES
    template_name = "academica/inscripcion_confirm_cancel.html"

    def dispatch(self, request, *args, **kwargs):
        self.inscripcion = get_object_or_404(
            InscripcionDetalle,
            pk=kwargs["id_inscripcion"],
        )
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        updated_rows = cancel_inscripcion(
            id_inscripcion=self.inscripcion.id_inscripcion,
            id_facultad=self.inscripcion.id_facultad,
        )
        if updated_rows:
            registrar_auditoria(
                request.user,
                "CANCELAR_INSCRIPCION",
                f"Inscripcion cancelada: {self.inscripcion.id_inscripcion}",
                esquema_afectado="fdw_*",
                tabla_afectada="inscripcion",
            )
            messages.success(request, "Inscripcion marcada como Cancelada.")
        else:
            messages.warning(request, "No se encontro la inscripcion para cancelar.")
        return redirect("academica:inscripcion_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["inscripcion"] = self.inscripcion
        return context


class ReadOnlyRedirectView(LoginRequiredMixin, View):
    redirect_url_name = "academica:inscripcion_list"

    def get(self, request, *args, **kwargs):
        messages.warning(request, READ_ONLY_MESSAGE)
        return redirect(self.redirect_url_name)

    def post(self, request, *args, **kwargs):
        messages.warning(request, READ_ONLY_MESSAGE)
        return redirect(self.redirect_url_name)


class AsignaturaDetailView(ReadOnlyRedirectView):
    redirect_url_name = "academica:asignatura_list"


class ProfesorDetailView(ReadOnlyRedirectView):
    redirect_url_name = "academica:profesor_list"


class PlanEstudiosListView(ReadOnlyRedirectView):
    redirect_url_name = "academica:asignatura_list"


class PreRequisitoListView(ReadOnlyRedirectView):
    redirect_url_name = "academica:asignatura_list"


class NotaGrupoListView(ReadOnlyRedirectView):
    redirect_url_name = "academica:grupo_list"


class NotaGrupoDetailView(ReadOnlyRedirectView):
    redirect_url_name = "academica:grupo_list"


class NotaInscripcionUpdateView(ReadOnlyRedirectView):
    redirect_url_name = "academica:inscripcion_list"
