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


class AsignaturaListView(LoginRequiredMixin, ListView):
    model = Asignatura
    template_name = "academica/asignatura_list.html"
    context_object_name = "asignaturas"


class AsignaturaDetailView(LoginRequiredMixin, DetailView):
    model = Asignatura
    template_name = "academica/asignatura_detail.html"
    context_object_name = "asignatura"
    pk_url_kwarg = "cod_asignatura"

    def get_queryset(self):
        plan_queryset = ProgramaAsignatura.objects.select_related(
            "programa_academico",
            "programa_academico__facultad",
        )
        return Asignatura.objects.prefetch_related(
            Prefetch("programas", queryset=plan_queryset),
        )


class PlanEstudiosListView(LoginRequiredMixin, ListView):
    model = ProgramaAsignatura
    template_name = "academica/plan_estudios_list.html"
    context_object_name = "plan_asignaturas"

    def get_queryset(self):
        return ProgramaAsignatura.objects.select_related(
            "programa_academico",
            "programa_academico__facultad",
            "asignatura",
        ).order_by(
            "programa_academico__nombre_programa",
            "semestre_sugerido",
            "asignatura__nombre_asignatura",
        )


class PreRequisitoListView(LoginRequiredMixin, ListView):
    model = PreRequisito
    template_name = "academica/prerequisito_list.html"
    context_object_name = "prerrequisitos"

    def get_queryset(self):
        return PreRequisito.objects.select_related(
            "programa_academico",
            "programa_asignatura__asignatura",
            "programa_asignatura_requisito__asignatura",
        ).order_by(
            "programa_academico__nombre_programa",
            "programa_asignatura__semestre_sugerido",
            "programa_asignatura__asignatura__nombre_asignatura",
        )


class ProfesorListView(LoginRequiredMixin, ListView):
    model = Profesor
    template_name = "academica/profesor_list.html"
    context_object_name = "profesores"

    def get_queryset(self):
        decanatura_queryset = Decano.objects.select_related(
            "facultad",
            "periodo_academico",
        )
        coordinacion_queryset = Coordinador.objects.select_related(
            "programa_academico",
            "programa_academico__facultad",
            "periodo_academico",
        )
        return (
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
            .order_by("usuario__nombre")
        )


class ProfesorDetailView(LoginRequiredMixin, DetailView):
    model = Profesor
    template_name = "academica/profesor_detail.html"
    context_object_name = "profesor"
    pk_url_kwarg = "id_profesor"

    def get_queryset(self):
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
        return Profesor.objects.select_related("usuario", "facultad").prefetch_related(
            Prefetch("grupos", queryset=grupo_queryset),
            Prefetch("decanaturas", queryset=decanatura_queryset),
            Prefetch("coordinaciones", queryset=coordinacion_queryset),
        )


class GrupoListView(LoginRequiredMixin, ListView):
    model = Grupo
    template_name = "academica/grupo_list.html"
    context_object_name = "grupos"

    def get_queryset(self):
        return (
            Grupo.objects.select_related(
                "programa_asignatura__asignatura",
                "programa_asignatura__programa_academico",
                "periodo_academico",
                "profesor__usuario",
            )
            .annotate(total_inscritos=Count("inscripciones"))
            .annotate(cupos_disponibles=F("cupo_maximo") - F("total_inscritos"))
            .order_by(
                "periodo_academico__id_periodo_academico",
                "programa_asignatura__programa_academico__nombre_programa",
                "programa_asignatura__asignatura__nombre_asignatura",
                "codigo_grupo",
            )
        )


class GrupoDetailView(LoginRequiredMixin, DetailView):
    model = Grupo
    template_name = "academica/grupo_detail.html"
    context_object_name = "grupo"
    pk_url_kwarg = "id_grupo"

    def get_queryset(self):
        inscripcion_queryset = Inscripcion.objects.select_related(
            "estudiante__usuario",
        ).order_by(
            "estudiante__usuario__nombre",
            "estudiante__id_estudiante",
        )
        return Grupo.objects.select_related(
            "programa_asignatura__asignatura",
            "programa_asignatura__programa_academico",
            "periodo_academico",
            "profesor__usuario",
        ).prefetch_related(
            Prefetch("inscripciones", queryset=inscripcion_queryset),
        )


class InscripcionListView(LoginRequiredMixin, ListView):
    model = Inscripcion
    template_name = "academica/inscripcion_list.html"
    context_object_name = "inscripciones"

    def get_queryset(self):
        return Inscripcion.objects.select_related(
            "estudiante__usuario",
            "grupo__programa_asignatura__asignatura",
            "grupo__programa_asignatura__programa_academico",
            "grupo__periodo_academico",
            "grupo__profesor__usuario",
        ).order_by(
            "grupo__periodo_academico__id_periodo_academico",
            "grupo__programa_asignatura__programa_academico__nombre_programa",
            "grupo__programa_asignatura__asignatura__nombre_asignatura",
            "estudiante__usuario__nombre",
        )
