from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Prefetch
from django.views.generic import DetailView, ListView

from apps.academica.models import (
    Asignatura,
    Coordinador,
    Decano,
    Grupo,
    Inscripcion,
    PreRequisito,
    Profesor,
    ProgramaAsignatura,
)
from apps.accounts.access import (
    STRUCTURE_ROLES,
    STUDENT_ROLES,
    TEACHING_ROLES,
    RoleRequiredMixin,
)
from apps.accounts.roles import get_user_roles
from apps.accounts.scope import (
    get_visible_group_ids,
    get_visible_professor_ids,
    get_visible_program_ids,
    get_visible_student_ids,
    is_superadmin,
)


class AsignaturaListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = (*STUDENT_ROLES, "docente")
    model = Asignatura
    template_name = "academica/asignatura_list.html"
    context_object_name = "asignaturas"

    def get_queryset(self):
        program_ids = get_visible_program_ids(
            self.request.user,
            include_student=True,
            include_teacher=True,
        )
        queryset = Asignatura.objects.all()
        if program_ids is None:
            return queryset
        return queryset.filter(
            programas__programa_academico_id__in=program_ids
        ).distinct()


class AsignaturaDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    allowed_roles = (*STUDENT_ROLES, "docente")
    model = Asignatura
    template_name = "academica/asignatura_detail.html"
    context_object_name = "asignatura"
    pk_url_kwarg = "cod_asignatura"

    def get_queryset(self):
        program_ids = get_visible_program_ids(
            self.request.user,
            include_student=True,
            include_teacher=True,
        )
        plan_queryset = ProgramaAsignatura.objects.select_related(
            "programa_academico",
            "programa_academico__facultad",
        )
        queryset = Asignatura.objects.prefetch_related(
            Prefetch("programas", queryset=plan_queryset),
        )
        if program_ids is None:
            return queryset
        return queryset.filter(
            programas__programa_academico_id__in=program_ids
        ).distinct()


class PlanEstudiosListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = (*STUDENT_ROLES, "docente")
    model = ProgramaAsignatura
    template_name = "academica/plan_estudios_list.html"
    context_object_name = "plan_asignaturas"

    def get_queryset(self):
        program_ids = get_visible_program_ids(
            self.request.user,
            include_student=True,
            include_teacher=True,
        )
        queryset = ProgramaAsignatura.objects.select_related(
            "programa_academico",
            "programa_academico__facultad",
            "asignatura",
        )
        if program_ids is not None:
            queryset = queryset.filter(programa_academico_id__in=program_ids)
        return queryset.order_by(
            "programa_academico__nombre_programa",
            "semestre_sugerido",
            "asignatura__nombre_asignatura",
        )


class PreRequisitoListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = STRUCTURE_ROLES
    model = PreRequisito
    template_name = "academica/prerequisito_list.html"
    context_object_name = "prerrequisitos"

    def get_queryset(self):
        program_ids = get_visible_program_ids(self.request.user)
        queryset = PreRequisito.objects.select_related(
            "programa_academico",
            "programa_asignatura__asignatura",
            "programa_asignatura_requisito__asignatura",
        )
        if program_ids is not None:
            queryset = queryset.filter(programa_academico_id__in=program_ids)
        return queryset.order_by(
            "programa_academico__nombre_programa",
            "programa_asignatura__semestre_sugerido",
            "programa_asignatura__asignatura__nombre_asignatura",
        )


class ProfesorListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = TEACHING_ROLES
    model = Profesor
    template_name = "academica/profesor_list.html"
    context_object_name = "profesores"

    def get_queryset(self):
        professor_ids = get_visible_professor_ids(self.request.user)
        decanatura_queryset = Decano.objects.select_related(
            "facultad",
            "periodo_academico",
        )
        coordinacion_queryset = Coordinador.objects.select_related(
            "programa_academico",
            "programa_academico__facultad",
            "periodo_academico",
        )
        queryset = (
            Profesor.objects.select_related("usuario", "facultad")
            .prefetch_related(
                Prefetch("decanaturas", queryset=decanatura_queryset),
                Prefetch("coordinaciones", queryset=coordinacion_queryset),
            )
            .annotate(
                total_grupos=Count("grupos", distinct=True),
                total_decanaturas=Count("decanaturas", distinct=True),
                total_coordinaciones=Count("coordinaciones", distinct=True),
            )
        )
        if professor_ids is not None:
            queryset = queryset.filter(id_profesor__in=professor_ids)
        return queryset.order_by("usuario__nombre")


class ProfesorDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    allowed_roles = TEACHING_ROLES
    model = Profesor
    template_name = "academica/profesor_detail.html"
    context_object_name = "profesor"
    pk_url_kwarg = "id_profesor"

    def get_queryset(self):
        professor_ids = get_visible_professor_ids(self.request.user)
        grupo_queryset = Grupo.objects.select_related(
            "programa_asignatura__asignatura",
            "programa_asignatura__programa_academico",
            "periodo_academico",
        ).order_by(
            "periodo_academico__id_periodo_academico",
            "programa_asignatura__programa_academico__nombre_programa",
            "programa_asignatura__asignatura__nombre_asignatura",
            "codigo_grupo",
        )
        decanatura_queryset = Decano.objects.select_related(
            "facultad",
            "periodo_academico",
        ).order_by("periodo_academico__id_periodo_academico")
        coordinacion_queryset = Coordinador.objects.select_related(
            "programa_academico",
            "programa_academico__facultad",
            "periodo_academico",
        ).order_by(
            "periodo_academico__id_periodo_academico",
            "programa_academico__nombre_programa",
        )
        queryset = Profesor.objects.select_related(
            "usuario", "facultad"
        ).prefetch_related(
            Prefetch("grupos", queryset=grupo_queryset),
            Prefetch("decanaturas", queryset=decanatura_queryset),
            Prefetch("coordinaciones", queryset=coordinacion_queryset),
        )
        if professor_ids is not None:
            queryset = queryset.filter(id_profesor__in=professor_ids)
        return queryset


class GrupoListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = TEACHING_ROLES
    model = Grupo
    template_name = "academica/grupo_list.html"
    context_object_name = "grupos"

    def get_queryset(self):
        group_ids = get_visible_group_ids(self.request.user)
        queryset = (
            Grupo.objects.select_related(
                "programa_asignatura__asignatura",
                "programa_asignatura__programa_academico",
                "periodo_academico",
                "profesor__usuario",
            )
            .annotate(total_inscritos=Count("inscripciones"))
            .annotate(cupos_disponibles=F("cupo_maximo") - F("total_inscritos"))
        )
        if group_ids is not None:
            queryset = queryset.filter(id_grupo__in=group_ids)
        return queryset.order_by(
            "periodo_academico__id_periodo_academico",
            "programa_asignatura__programa_academico__nombre_programa",
            "programa_asignatura__asignatura__nombre_asignatura",
            "codigo_grupo",
        )


class GrupoDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    allowed_roles = TEACHING_ROLES
    model = Grupo
    template_name = "academica/grupo_detail.html"
    context_object_name = "grupo"
    pk_url_kwarg = "id_grupo"

    def get_queryset(self):
        group_ids = get_visible_group_ids(self.request.user)
        inscripcion_queryset = Inscripcion.objects.select_related(
            "estudiante__usuario",
        ).order_by(
            "estudiante__usuario__nombre",
            "estudiante__id_estudiante",
        )
        queryset = Grupo.objects.select_related(
            "programa_asignatura__asignatura",
            "programa_asignatura__programa_academico",
            "periodo_academico",
            "profesor__usuario",
        ).prefetch_related(
            Prefetch("inscripciones", queryset=inscripcion_queryset),
        )
        if group_ids is not None:
            queryset = queryset.filter(id_grupo__in=group_ids)
        return queryset


class InscripcionListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = (*STUDENT_ROLES, "docente")
    model = Inscripcion
    template_name = "academica/inscripcion_list.html"
    context_object_name = "inscripciones"

    def get_queryset(self):
        base_queryset = Inscripcion.objects.select_related(
            "estudiante__usuario",
            "grupo__programa_asignatura__asignatura",
            "grupo__programa_asignatura__programa_academico",
            "grupo__periodo_academico",
            "grupo__profesor__usuario",
        )
        if is_superadmin(self.request.user):
            queryset = base_queryset
        elif "estudiante" in get_user_roles(self.request.user):
            queryset = base_queryset.filter(estudiante__usuario=self.request.user)
        else:
            student_ids = get_visible_student_ids(self.request.user)
            group_ids = get_visible_group_ids(self.request.user)
            queryset = base_queryset.none()
            if student_ids:
                queryset = queryset | base_queryset.filter(
                    estudiante_id__in=student_ids
                )
            if group_ids:
                queryset = queryset | base_queryset.filter(grupo_id__in=group_ids)
        return queryset.distinct().order_by(
            "grupo__periodo_academico__id_periodo_academico",
            "grupo__programa_asignatura__programa_academico__nombre_programa",
            "grupo__programa_asignatura__asignatura__nombre_asignatura",
            "estudiante__usuario__nombre",
        )
