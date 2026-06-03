from django.contrib import admin

from apps.homologaciones.models import HomologacionGlobal


class SoloLecturaAdminMixin:
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HomologacionGlobal)
class HomologacionGlobalAdmin(SoloLecturaAdminMixin, admin.ModelAdmin):
    list_display = (
        "asignatura_origen",
        "institucion_origen",
        "estado_homologacion",
        "fecha_solicitud",
        "fecha_respuesta",
        "nota_obtenida",
        "nodo_origen",
    )
    list_filter = ("estado_homologacion", "fecha_solicitud", "nodo_origen")
    search_fields = ("asignatura_origen", "institucion_origen", "observacion")
