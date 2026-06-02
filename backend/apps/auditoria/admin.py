from django.contrib import admin

from apps.auditoria.models import Auditoria


class SoloLecturaAdminMixin:
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Auditoria)
class AuditoriaAdmin(SoloLecturaAdminMixin, admin.ModelAdmin):
    list_display = ("usuario", "accion_realizada", "fecha_hora", "descripcion")
    list_filter = ("accion_realizada", "fecha_hora")
    search_fields = (
        "usuario__nombre",
        "usuario__correo",
        "accion_realizada",
        "descripcion",
    )
    list_select_related = ("usuario",)
    date_hierarchy = "fecha_hora"
