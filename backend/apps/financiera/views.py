from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from apps.financiera.models import Matricula, Recibo, TarifaMatricula


class TarifaMatriculaListView(LoginRequiredMixin, ListView):
    model = TarifaMatricula
    template_name = "financiera/tarifa_list.html"
    context_object_name = "tarifas"

    def get_queryset(self):
        return TarifaMatricula.objects.select_related(
            "programa_academico",
            "programa_academico__facultad",
            "periodo_academico",
        )


class ReciboListView(LoginRequiredMixin, ListView):
    model = Recibo
    template_name = "financiera/recibo_list.html"
    context_object_name = "recibos"

    def get_queryset(self):
        return Recibo.objects.select_related(
            "estudiante__usuario",
            "estudiante__programa_academico",
            "tarifa_matricula__programa_academico",
            "tarifa_matricula__periodo_academico",
        )


class ReciboDetailView(LoginRequiredMixin, DetailView):
    model = Recibo
    template_name = "financiera/recibo_detail.html"
    context_object_name = "recibo"
    pk_url_kwarg = "id_recibo"

    def get_queryset(self):
        return Recibo.objects.select_related(
            "estudiante__usuario",
            "estudiante__programa_academico",
            "tarifa_matricula__programa_academico",
            "tarifa_matricula__periodo_academico",
        )


class MatriculaListView(LoginRequiredMixin, ListView):
    model = Matricula
    template_name = "financiera/matricula_list.html"
    context_object_name = "matriculas"

    def get_queryset(self):
        return Matricula.objects.select_related(
            "recibo__estudiante__usuario",
            "recibo__estudiante__programa_academico",
            "recibo__tarifa_matricula__programa_academico",
            "recibo__tarifa_matricula__periodo_academico",
        )


class MatriculaDetailView(LoginRequiredMixin, DetailView):
    model = Matricula
    template_name = "financiera/matricula_detail.html"
    context_object_name = "matricula"
    pk_url_kwarg = "id_matricula"

    def get_queryset(self):
        return Matricula.objects.select_related(
            "recibo__estudiante__usuario",
            "recibo__estudiante__programa_academico",
            "recibo__tarifa_matricula__programa_academico",
            "recibo__tarifa_matricula__periodo_academico",
        )
