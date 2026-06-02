from django.contrib import admin

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


class SoloLecturaAdminMixin:
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Asignatura)
class AsignaturaAdmin(SoloLecturaAdminMixin, admin.ModelAdmin):
    list_display = (
        "cod_asignatura",
        "nombre_asignatura",
        "creditos",
        "estado",
        "homologable",
    )
    list_filter = ("estado", "homologable")
    search_fields = ("cod_asignatura", "nombre_asignatura")


@admin.register(ProgramaAsignatura)
class ProgramaAsignaturaAdmin(SoloLecturaAdminMixin, admin.ModelAdmin):
    list_display = (
        "programa_academico",
        "asignatura",
        "semestre_sugerido",
        "tipo_asignatura",
        "estado",
    )
    list_filter = ("estado", "tipo_asignatura", "programa_academico")
    search_fields = (
        "programa_academico__nombre_programa",
        "asignatura__nombre_asignatura",
        "asignatura__cod_asignatura",
    )
    list_select_related = ("programa_academico", "asignatura")


@admin.register(PreRequisito)
class PreRequisitoAdmin(SoloLecturaAdminMixin, admin.ModelAdmin):
    list_display = (
        "programa_academico",
        "programa_asignatura",
        "programa_asignatura_requisito",
    )
    list_filter = ("programa_academico",)
    list_select_related = (
        "programa_academico",
        "programa_asignatura__asignatura",
        "programa_asignatura_requisito__asignatura",
    )


@admin.register(Profesor)
class ProfesorAdmin(SoloLecturaAdminMixin, admin.ModelAdmin):
    list_display = ("usuario", "facultad", "categoria", "vinculacion")
    list_filter = ("facultad", "categoria", "vinculacion")
    search_fields = ("usuario__nombre", "usuario__correo", "facultad__nombre_facultad")
    list_select_related = ("usuario", "facultad")


@admin.register(Decano)
class DecanoAdmin(SoloLecturaAdminMixin, admin.ModelAdmin):
    list_display = ("profesor", "facultad", "periodo_academico")
    list_filter = ("facultad", "periodo_academico")
    search_fields = ("profesor__usuario__nombre", "facultad__nombre_facultad")
    list_select_related = ("profesor__usuario", "facultad", "periodo_academico")


@admin.register(Coordinador)
class CoordinadorAdmin(SoloLecturaAdminMixin, admin.ModelAdmin):
    list_display = ("profesor", "programa_academico", "periodo_academico")
    list_filter = ("programa_academico", "periodo_academico")
    search_fields = (
        "profesor__usuario__nombre",
        "programa_academico__nombre_programa",
    )
    list_select_related = (
        "profesor__usuario",
        "programa_academico",
        "periodo_academico",
    )


@admin.register(Grupo)
class GrupoAdmin(SoloLecturaAdminMixin, admin.ModelAdmin):
    list_display = (
        "codigo_grupo",
        "programa_asignatura",
        "periodo_academico",
        "cupo_maximo",
        "estado_grupo",
        "profesor",
    )
    list_filter = ("estado_grupo", "periodo_academico")
    search_fields = (
        "codigo_grupo",
        "programa_asignatura__asignatura__nombre_asignatura",
    )
    list_select_related = (
        "programa_asignatura__asignatura",
        "programa_asignatura__programa_academico",
        "periodo_academico",
        "profesor__usuario",
    )


@admin.register(Inscripcion)
class InscripcionAdmin(SoloLecturaAdminMixin, admin.ModelAdmin):
    list_display = (
        "estudiante",
        "grupo",
        "estado_inscripcion",
        "nota_final",
        "intento",
    )
    list_filter = ("estado_inscripcion", "grupo__periodo_academico")
    search_fields = (
        "estudiante__id_estudiante",
        "estudiante__usuario__nombre",
        "grupo__codigo_grupo",
    )
    list_select_related = (
        "estudiante__usuario",
        "grupo__programa_asignatura__asignatura",
        "grupo__programa_asignatura__programa_academico",
        "grupo__periodo_academico",
    )
