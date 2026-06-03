from django.contrib import admin

from apps.financiera.models import MatriculaDetalle, Recibo, TarifaMatricula


class SoloLecturaAdminMixin:
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TarifaMatricula)
class TarifaMatriculaAdmin(SoloLecturaAdminMixin, admin.ModelAdmin):
    list_display = (
        "programa_academico",
        "periodo_academico",
        "valor_matricula",
        "fecha_limite_ordinaria",
        "fecha_limite_extraordinaria",
        "estado",
    )
    list_filter = ("estado", "periodo_academico", "programa_academico")
    search_fields = ("programa_academico__nombre_programa",)
    list_select_related = ("programa_academico", "periodo_academico")


@admin.register(Recibo)
class ReciboAdmin(SoloLecturaAdminMixin, admin.ModelAdmin):
    list_display = (
        "id_estudiante",
        "tarifa_matricula",
        "estado_pago",
        "valor_pagado",
        "fecha_pago",
        "metodo_pago",
    )
    list_filter = ("estado_pago", "metodo_pago", "tarifa_matricula__periodo_academico")
    search_fields = ("id_estudiante",)
    list_select_related = (
        "tarifa_matricula__programa_academico",
        "tarifa_matricula__periodo_academico",
    )


@admin.register(MatriculaDetalle)
class MatriculaDetalleAdmin(SoloLecturaAdminMixin, admin.ModelAdmin):
    list_display = (
        "estudiante",
        "nombre_facultad",
        "nombre_programa",
        "id_periodo_academico",
        "estado_matricula",
        "estado_pago",
    )
    list_filter = ("estado_matricula", "estado_pago", "id_periodo_academico")
    search_fields = ("estudiante", "nombre_programa", "nombre_facultad")
