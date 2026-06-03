from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView, View

from apps.academica.distributed_write import (
    deactivate_or_cancel_grupo,
    delete_or_deactivate_estudiante,
)
from apps.academica.forms import (
    EstudianteCreateForm,
    EstudianteUpdateForm,
    GrupoCreateForm,
    GrupoUpdateForm,
    user_can_create_groups,
    user_can_create_students,
)
from apps.accounts.access import (
    STUDENT_ROLES,
    TEACHING_ROLES,
    RoleRequiredMixin,
)
from apps.estructura.models import Asignatura
from apps.reportes.models import (
    EstudianteDetalle,
    GrupoDetalle,
    InscripcionDetalle,
    ProfesorDetalle,
)

ACADEMIC_READ_ROLES = (*STUDENT_ROLES, "docente")
STUDENT_WRITE_ROLES = ("coordinador", "superadmin")
GROUP_WRITE_ROLES = ("coordinador", "superadmin")
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


class EstudianteListView(AcademicReportListView):
    allowed_roles = STUDENT_ROLES
    model = EstudianteDetalle
    template_name = "academica/estudiante_list.html"
    context_object_name = "estudiantes"
    filters = (
        "id_facultad",
        "nombre_facultad",
        "id_programa_academico",
        "nombre_programa",
        "estado_estudiante",
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_create_students"] = user_can_create_students(self.request.user)
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
        return kwargs

    def form_valid(self, form):
        form.save()
        # TODO: registrar auditoria distribuida cuando se consolide el contrato.
        messages.success(self.request, "Estudiante creado en el nodo distribuido.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Crear estudiante"
        context["submit_label"] = "Crear estudiante"
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
        return kwargs

    def form_valid(self, form):
        updated_rows = form.save()
        if updated_rows:
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
    filters = ("id_facultad", "nombre_facultad", "categoria", "vinculacion")


class GrupoListView(AcademicReportListView):
    allowed_roles = TEACHING_ROLES
    model = GrupoDetalle
    template_name = "academica/grupo_list.html"
    context_object_name = "grupos"
    filters = (
        "id_facultad",
        "nombre_facultad",
        "id_programa_academico",
        "nombre_programa",
        "id_periodo_academico",
        "estado_grupo",
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_create_groups"] = user_can_create_groups(self.request.user)
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
        return kwargs

    def form_valid(self, form):
        form.save()
        # TODO: registrar auditoria distribuida cuando se consolide el contrato.
        messages.success(self.request, "Grupo creado en el nodo distribuido.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Crear grupo"
        context["submit_label"] = "Crear grupo"
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
        return kwargs

    def form_valid(self, form):
        updated_rows = form.save()
        if updated_rows:
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
        "nombre_facultad",
        "id_programa_academico",
        "nombre_programa",
        "id_periodo_academico",
        "estado_inscripcion",
    )


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


class InscripcionCreateView(ReadOnlyRedirectView):
    redirect_url_name = "academica:inscripcion_list"


class InscripcionCancelView(ReadOnlyRedirectView):
    redirect_url_name = "academica:inscripcion_list"


class NotaGrupoListView(ReadOnlyRedirectView):
    redirect_url_name = "academica:grupo_list"


class NotaGrupoDetailView(ReadOnlyRedirectView):
    redirect_url_name = "academica:grupo_list"


class NotaInscripcionUpdateView(ReadOnlyRedirectView):
    redirect_url_name = "academica:inscripcion_list"
