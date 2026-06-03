from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.db.models import Count, Q
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
    user_can_cancel_enrollments,
    user_can_create_enrollments,
    user_can_create_groups,
    user_can_create_students,
    user_can_edit_enrollments,
    user_can_write_enrollments,
)
from apps.accounts.access import (
    STUDENT_ROLES,
    TEACHING_ROLES,
    RoleRequiredMixin,
)
from apps.accounts.access_context import (
    filter_estudiantes_for_user,
    filter_grupos_for_user,
    filter_inscripciones_for_user,
    filter_profesores_for_user,
    get_access_context,
)
from apps.auditoria.services import registrar_auditoria
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

ACADEMIC_READ_ROLES = (*STUDENT_ROLES, "docente", "administrativo")
STUDENT_WRITE_ROLES = ("coordinador", "superadmin")
GROUP_WRITE_ROLES = ("coordinador", "superadmin")
ENROLLMENT_WRITE_ROLES = ("estudiante", "coordinador", "decano", "superadmin")
ENROLLMENT_EDIT_ROLES = ("estudiante", "docente", "coordinador", "decano", "superadmin")
READ_ONLY_MESSAGE = (
    "Esta pantalla es de consulta consolidada; usa las acciones disponibles del modulo."
)
CURRENT_ENROLLMENT_STATES = {"Cursando"}
HISTORY_ENROLLMENT_STATES = {"Aprobada", "Reprobada", "Cancelada", "Finalizada"}


def _subject_codes_for_user(user):
    context = get_access_context(user)
    if context.is_superadmin:
        return None
    if not context.program_ids:
        return []
    with connection.cursor() as cursor:
        cursor.execute(
            """
            select distinct cod_asignatura
            from reportes.vw_programa_asignatura_global
            where id_programa_academico = any(%s)
              and estado = 'Activa'
            """,
            [list(context.program_ids)],
        )
        return [row[0] for row in cursor.fetchall()]


def _program_ids_for_request(request):
    user = request.user
    context = get_access_context(user)
    if context.is_superadmin:
        selected_program = request.GET.get("id_programa_academico")
        return [selected_program] if selected_program else None
    return list(context.program_ids)


def _current_period_ids():
    with connection.cursor() as cursor:
        cursor.execute(
            """
            select id_periodo_academico
            from institucional.periodo_academico
            where estado = 'Activo'
            order by fecha_inicio desc, id_periodo_academico
            """
        )
        return [row[0] for row in cursor.fetchall()]


def _fetch_program_subject_rows(program_ids=None, status=None):
    where = []
    params = []
    if program_ids is not None:
        if not program_ids:
            return []
        where.append("pa.id_programa_academico = any(%s)")
        params.append(program_ids)
    if status:
        where.append("pa.estado = %s")
        params.append(status)
    where_sql = f"where {' and '.join(where)}" if where else ""
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            select
                pa.id_programa_asignatura,
                pa.id_facultad,
                coalesce(f.nombre_facultad, pa.id_facultad) as nombre_facultad,
                pa.id_programa_academico,
                coalesce(p.nombre_programa, pa.id_programa_academico)
                    as nombre_programa,
                pa.cod_asignatura,
                coalesce(a.nombre_asignatura, pa.cod_asignatura)
                    as nombre_asignatura,
                a.creditos,
                a.horas_teoria,
                a.horas_pract,
                a.homologable,
                pa.semestre_sugerido,
                pa.tipo_asignatura,
                pa.estado
            from reportes.vw_programa_asignatura_global pa
            left join institucional.facultad f
              on f.id_facultad = pa.id_facultad
            left join institucional.programa_academico p
              on p.id_programa_academico = pa.id_programa_academico
            left join institucional.asignatura a
              on a.cod_asignatura = pa.cod_asignatura
            {where_sql}
            order by nombre_programa, pa.semestre_sugerido,
                     nombre_asignatura, pa.cod_asignatura
            """,
            params,
        )
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]


def _group_count_by_group(group_ids):
    if not group_ids:
        return {}
    rows = (
        InscripcionDetalle.objects.filter(id_grupo__in=group_ids)
        .exclude(estado_inscripcion="Cancelada")
        .values("id_grupo")
        .annotate(total=Count("id_inscripcion"))
    )
    return {row["id_grupo"]: row["total"] for row in rows}


def _attach_group_counts(groups):
    counts = _group_count_by_group([group.id_grupo for group in groups])
    for group in groups:
        group.inscritos_actuales = counts.get(group.id_grupo, 0)
    return groups


def _group_rows(rows, key):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row[key]].append(row)
    return grouped.items()


def _student_can_request_group(user, group):
    context = get_access_context(user)
    if "estudiante" not in context.roles or not context.student_ids:
        return False
    if group.estado_grupo not in {"Abierto", "En curso"}:
        return False
    if group.id_programa_academico not in context.program_ids:
        return False
    student_ids = list(context.student_ids)
    approved = InscripcionDetalle.objects.filter(
        Q(estado_inscripcion="Aprobada") | Q(nota_final__gte=3),
        id_estudiante__in=student_ids,
        id_programa_academico=group.id_programa_academico,
        cod_asignatura=group.cod_asignatura,
    ).exists()
    if approved:
        return False
    active_same_period = InscripcionDetalle.objects.filter(
        id_estudiante__in=student_ids,
        cod_asignatura=group.cod_asignatura,
        id_periodo_academico=group.id_periodo_academico,
        estado_inscripcion="Cursando",
    ).exists()
    if active_same_period:
        return False
    duplicate = InscripcionDetalle.objects.filter(
        id_estudiante__in=student_ids,
        id_grupo=group.id_grupo,
    ).exists()
    if duplicate:
        return False
    if (
        group.cupo_maximo is not None
        and getattr(group, "inscritos_actuales", 0) >= group.cupo_maximo
    ):
        return False
    return True


class AcademicReportListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    paginate_by = 25
    filters = ()
    access_filter = None

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.access_filter is not None:
            queryset = self.access_filter(queryset, self.request.user)
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


class AsignaturaListView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = ACADEMIC_READ_ROLES
    template_name = "academica/asignatura_list.html"

    def get_program_ids(self):
        return _program_ids_for_request(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        status = self.request.GET.get("estado", "Activa")
        status_filter = status or None
        context["list_title"] = getattr(self, "list_title", "Asignaturas")
        context["asignaturas_programa"] = _fetch_program_subject_rows(
            self.get_program_ids(),
            status=status_filter,
        )
        context["estado_choices"] = [
            ("", "Todos"),
            ("Activa", "Activa"),
            ("Inactiva", "Inactiva"),
        ]
        context["active_filters"] = {
            "estado": status,
            "id_programa_academico": self.request.GET.get("id_programa_academico", ""),
        }
        context["programa_choices"] = programa_choices()
        return context


class PlanEstudiosListView(AsignaturaListView):
    template_name = "academica/plan_estudios_list.html"
    list_title = "Plan de estudios"

    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        rows = _fetch_program_subject_rows(self.get_program_ids())
        context["list_title"] = self.list_title
        context["asignaturas_programa"] = rows
        context["programa_choices"] = programa_choices()
        context["active_filters"] = {
            "id_programa_academico": self.request.GET.get("id_programa_academico", ""),
        }
        rows = context["asignaturas_programa"]
        programs = []
        for program_key, program_rows in _group_rows(rows, "id_programa_academico"):
            program_rows = list(program_rows)
            semesters = []
            for semester_key, semester_rows in _group_rows(
                program_rows,
                "semestre_sugerido",
            ):
                semesters.append(
                    {
                        "semestre": semester_key,
                        "materias": list(semester_rows),
                    }
                )
            first_row = program_rows[0]
            total_credits = sum(row["creditos"] or 0 for row in program_rows)
            semester_count = len(
                {
                    row["semestre_sugerido"]
                    for row in program_rows
                    if row["semestre_sugerido"] is not None
                },
            )
            programs.append(
                {
                    "id_programa_academico": program_key,
                    "nombre_programa": first_row["nombre_programa"],
                    "id_facultad": first_row["id_facultad"],
                    "nombre_facultad": first_row["nombre_facultad"],
                    "total_materias": len(program_rows),
                    "total_creditos": total_credits,
                    "total_semestres": semester_count,
                    "semestres": semesters,
                }
            )
        context["programas_plan"] = programs
        return context


class EstudianteListView(AcademicReportListView):
    allowed_roles = (*STUDENT_ROLES, "administrativo")
    model = EstudianteDetalle
    template_name = "academica/estudiante_list.html"
    context_object_name = "estudiantes"
    access_filter = staticmethod(filter_estudiantes_for_user)
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
    allowed_roles = (*STUDENT_ROLES, "administrativo")
    model = EstudianteDetalle
    template_name = "academica/estudiante_detail.html"
    context_object_name = "estudiante"
    pk_url_kwarg = "id_estudiante"

    def get_queryset(self):
        return filter_estudiantes_for_user(super().get_queryset(), self.request.user)

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
            filter_estudiantes_for_user(EstudianteDetalle.objects.all(), request.user),
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
            filter_estudiantes_for_user(EstudianteDetalle.objects.all(), request.user),
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
    allowed_roles = (*TEACHING_ROLES, "administrativo")
    model = ProfesorDetalle
    template_name = "academica/profesor_list.html"
    context_object_name = "profesores"
    filters = ("id_facultad", "categoria", "vinculacion")
    access_filter = staticmethod(filter_profesores_for_user)

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
    allowed_roles = (*TEACHING_ROLES, "administrativo")
    model = GrupoDetalle
    template_name = "academica/grupo_list.html"
    context_object_name = "grupos"
    access_filter = staticmethod(filter_grupos_for_user)
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
    allowed_roles = ACADEMIC_READ_ROLES
    model = GrupoDetalle
    template_name = "academica/grupo_detail.html"
    context_object_name = "grupo"
    pk_url_kwarg = "id_grupo"

    def get_queryset(self):
        context = get_access_context(self.request.user)
        student_only = (
            "estudiante" in context.roles
            and not context.roles.intersection({"coordinador", "decano", "superadmin"})
        )
        if student_only:
            return super().get_queryset().filter(
                id_programa_academico__in=context.program_ids,
            )
        return filter_grupos_for_user(super().get_queryset(), self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_create_groups"] = user_can_create_groups(self.request.user)
        inscritos = list(
            filter_inscripciones_for_user(
                InscripcionDetalle.objects.filter(id_grupo=self.object.id_grupo),
                self.request.user,
            ).order_by("estudiante", "id_inscripcion")
        )
        can_view_group_notes = self._can_view_group_notes()
        student_ids = get_access_context(self.request.user).student_ids
        for inscripcion in inscritos:
            inscripcion.can_view_note = can_view_group_notes or (
                inscripcion.id_estudiante in student_ids
            )
        context["inscripciones_grupo"] = inscritos
        context["can_view_group_notes"] = can_view_group_notes
        return context

    def _can_view_group_notes(self):
        context = get_access_context(self.request.user)
        if context.is_superadmin:
            return True
        if (
            "docente" in context.roles
            and self.object.id_profesor in context.professor_ids
        ):
            return True
        if (
            "coordinador" in context.roles
            and self.object.id_programa_academico in context.coordinated_program_ids
        ):
            return True
        return (
            "decano" in context.roles
            and self.object.id_facultad in context.dean_faculty_ids
        )


class GruposAsignaturaListView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = ACADEMIC_READ_ROLES
    template_name = "academica/grupos_asignatura_list.html"

    def dispatch(self, request, *args, **kwargs):
        self.plan_row = self._get_plan_row()
        if self.plan_row is None:
            raise PermissionDenied("La asignatura esta fuera de tu alcance.")
        return super().dispatch(request, *args, **kwargs)

    def _get_plan_row(self):
        program_ids = _program_ids_for_request(self.request)
        rows = _fetch_program_subject_rows(program_ids, status="Activa")
        id_programa_asignatura = str(self.kwargs.get("id_programa_asignatura", ""))
        cod_asignatura = self.kwargs.get("cod_asignatura")
        for row in rows:
            if id_programa_asignatura and str(row["id_programa_asignatura"]) == (
                id_programa_asignatura
            ):
                return row
            if cod_asignatura and row["cod_asignatura"] == cod_asignatura:
                return row
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = GrupoDetalle.objects.filter(
            id_programa_asignatura=self.plan_row["id_programa_asignatura"],
        ).exclude(estado_grupo__in=["Cancelado", "Finalizado"])
        current_period_ids = _current_period_ids()
        if current_period_ids:
            queryset = queryset.filter(id_periodo_academico__in=current_period_ids)
        context_access = get_access_context(self.request.user)
        student_only = (
            "estudiante" in context_access.roles
            and not context_access.roles.intersection(
                {"coordinador", "decano", "superadmin"},
            )
        )
        if not student_only:
            queryset = filter_grupos_for_user(queryset, self.request.user)
        grupos = _attach_group_counts(list(queryset))
        for grupo in grupos:
            grupo.can_request_enrollment = _student_can_request_group(
                self.request.user,
                grupo,
            )
        context["plan"] = self.plan_row
        context["grupos"] = grupos
        context["current_period_ids"] = current_period_ids
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
        self.grupo = get_object_or_404(
            filter_grupos_for_user(GrupoDetalle.objects.all(), request.user),
            pk=kwargs["id_grupo"],
        )
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
        self.grupo = get_object_or_404(
            filter_grupos_for_user(GrupoDetalle.objects.all(), request.user),
            pk=kwargs["id_grupo"],
        )
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
    access_filter = staticmethod(filter_inscripciones_for_user)
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
        context["can_create_enrollments"] = user_can_create_enrollments(
            self.request.user,
        )
        context["can_edit_enrollments"] = user_can_edit_enrollments(self.request.user)
        context["can_cancel_enrollments"] = user_can_cancel_enrollments(
            self.request.user,
        )
        context["student_enrollment_view"] = (
            "estudiante" in get_access_context(self.request.user).roles
            and not user_can_edit_enrollments(self.request.user)
        )
        if context["student_enrollment_view"]:
            object_list = list(context["inscripciones"])
            context["current_inscripciones"] = [
                item
                for item in object_list
                if item.estado_inscripcion in CURRENT_ENROLLMENT_STATES
            ]
            context["history_inscripciones"] = [
                item
                for item in object_list
                if item.estado_inscripcion in HISTORY_ENROLLMENT_STATES
                or item.estado_inscripcion not in CURRENT_ENROLLMENT_STATES
            ]
        context["history_page"] = getattr(self, "history_page", False)
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


class HistorialAcademicoView(InscripcionListView):
    history_page = True

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.exclude(estado_inscripcion__in=CURRENT_ENROLLMENT_STATES)


class InscripcionDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    allowed_roles = ACADEMIC_READ_ROLES
    model = InscripcionDetalle
    template_name = "academica/inscripcion_detail.html"
    context_object_name = "inscripcion"
    pk_url_kwarg = "id_inscripcion"

    def get_queryset(self):
        return filter_inscripciones_for_user(
            super().get_queryset(),
            self.request.user,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_write_enrollments"] = user_can_write_enrollments(
            self.request.user,
        )
        context["can_edit_enrollment"] = user_can_edit_enrollments(self.request.user)
        context["can_cancel_enrollment"] = (
            user_can_cancel_enrollments(self.request.user)
            and self.object.estado_inscripcion in CURRENT_ENROLLMENT_STATES
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
        kwargs["selected_group"] = self.request.GET.get("id_grupo")
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
        context["submit_label"] = "Solicitar inscripcion"
        is_student_flow = (
            "estudiante" in get_access_context(self.request.user).roles
            and not user_can_edit_enrollments(self.request.user)
        )
        if not is_student_flow:
            context["facultad_choices"] = facultad_choices("Seleccione facultad")
            context["periodo_choices"] = periodo_choices("Seleccione periodo")
        context["selected_facultad"] = self.request.GET.get("id_facultad", "")
        context["selected_periodo"] = self.request.GET.get(
            "id_periodo_academico",
            "",
        )
        return context


class InscripcionUpdateView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    allowed_roles = ENROLLMENT_EDIT_ROLES
    form_class = InscripcionUpdateForm
    template_name = "academica/inscripcion_form.html"
    success_url = reverse_lazy("academica:inscripcion_list")

    def dispatch(self, request, *args, **kwargs):
        if not user_can_edit_enrollments(request.user):
            raise PermissionDenied("Los estudiantes no pueden editar notas o estado.")
        self.inscripcion = get_object_or_404(
            filter_inscripciones_for_user(
                InscripcionDetalle.objects.all(),
                request.user,
            ),
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
            filter_inscripciones_for_user(
                InscripcionDetalle.objects.all(),
                request.user,
            ),
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


class PreRequisitoListView(ReadOnlyRedirectView):
    redirect_url_name = "academica:asignatura_list"


class NotaGrupoListView(ReadOnlyRedirectView):
    redirect_url_name = "academica:grupo_list"


class NotaGrupoDetailView(ReadOnlyRedirectView):
    redirect_url_name = "academica:grupo_list"


class NotaInscripcionUpdateView(ReadOnlyRedirectView):
    redirect_url_name = "academica:inscripcion_list"
