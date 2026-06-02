from django.contrib import admin

from apps.estructura.models import Facultad, PeriodoAcademico, ProgramaAcademico


class SoloLecturaAdminMixin:
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Facultad)
class FacultadAdmin(SoloLecturaAdminMixin, admin.ModelAdmin):
    list_display = (
        "id_facultad",
        "nombre_facultad",
        "ubicacion",
        "correo_institucional",
    )
    search_fields = ("id_facultad", "nombre_facultad", "correo_institucional")


@admin.register(ProgramaAcademico)
class ProgramaAcademicoAdmin(SoloLecturaAdminMixin, admin.ModelAdmin):
    list_display = (
        "id_programa_academico",
        "nombre_programa",
        "facultad",
        "estado",
        "modalidad",
        "nivel_formacion",
    )
    list_filter = ("estado", "modalidad", "nivel_formacion", "facultad")
    search_fields = (
        "id_programa_academico",
        "nombre_programa",
        "facultad__nombre_facultad",
    )
    list_select_related = ("facultad",)


@admin.register(PeriodoAcademico)
class PeriodoAcademicoAdmin(SoloLecturaAdminMixin, admin.ModelAdmin):
    list_display = ("id_periodo_academico", "fecha_inicio", "fecha_final", "estado")
    list_filter = ("estado",)
    search_fields = ("id_periodo_academico",)
