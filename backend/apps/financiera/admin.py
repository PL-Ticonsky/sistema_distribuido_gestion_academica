from django.contrib import admin

from apps.financiera.models import Matricula, Recibo, TarifaMatricula


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
        "estudiante",
        "tarifa_matricula",
        "estado_pago",
        "valor_pagado",
        "fecha_pago",
        "metodo_pago",
    )
    list_filter = ("estado_pago", "metodo_pago", "tarifa_matricula__periodo_academico")
    search_fields = (
        "estudiante__usuario__nombre",
        "estudiante__usuario__correo",
        "tarifa_matricula__programa_academico__nombre_programa",
    )
    list_select_related = (
        "estudiante__usuario",
        "tarifa_matricula__programa_academico",
        "tarifa_matricula__periodo_academico",
    )


@admin.register(Matricula)
class MatriculaAdmin(SoloLecturaAdminMixin, admin.ModelAdmin):
    list_display = ("recibo", "estado_matricula")
    list_filter = (
        "estado_matricula",
        "recibo__tarifa_matricula__periodo_academico",
    )
    search_fields = (
        "recibo__estudiante__usuario__nombre",
        "recibo__estudiante__usuario__correo",
    )
    list_select_related = (
        "recibo__estudiante__usuario",
        "recibo__tarifa_matricula__programa_academico",
        "recibo__tarifa_matricula__periodo_academico",
    )
