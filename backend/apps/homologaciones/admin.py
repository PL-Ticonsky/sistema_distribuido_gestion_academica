from django.contrib import admin

from apps.homologaciones.models import Homologacion


class SoloLecturaAdminMixin:
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Homologacion)
class HomologacionAdmin(SoloLecturaAdminMixin, admin.ModelAdmin):
    list_display = (
        "estudiante",
        "programa_asignatura",
        "profesor_evaluador",
        "estado_homologacion",
        "fecha_solicitud",
        "fecha_respuesta",
        "nota_obtenida",
    )
    list_filter = (
        "estado_homologacion",
        "fecha_solicitud",
        "programa_asignatura__programa_academico",
    )
    search_fields = (
        "estudiante__usuario__nombre",
        "estudiante__usuario__correo",
        "profesor_evaluador__usuario__nombre",
        "asignatura_origen",
        "institucion_origen",
        "programa_asignatura__asignatura__nombre_asignatura",
    )
    list_select_related = (
        "estudiante__usuario",
        "estudiante__programa_academico",
        "profesor_evaluador__usuario",
        "programa_asignatura__asignatura",
        "programa_asignatura__programa_academico",
    )
