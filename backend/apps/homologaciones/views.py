from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from apps.homologaciones.models import Homologacion


class HomologacionListView(LoginRequiredMixin, ListView):
    model = Homologacion
    template_name = "homologaciones/homologacion_list.html"
    context_object_name = "homologaciones"

    def get_queryset(self):
        return Homologacion.objects.select_related(
            "estudiante__usuario",
            "estudiante__programa_academico",
            "profesor_evaluador__usuario",
            "programa_asignatura__asignatura",
            "programa_asignatura__programa_academico",
        )


class HomologacionDetailView(LoginRequiredMixin, DetailView):
    model = Homologacion
    template_name = "homologaciones/homologacion_detail.html"
    context_object_name = "homologacion"
    pk_url_kwarg = "id_homologacion"

    def get_queryset(self):
        return Homologacion.objects.select_related(
            "estudiante__usuario",
            "estudiante__programa_academico",
            "profesor_evaluador__usuario",
            "programa_asignatura__asignatura",
            "programa_asignatura__programa_academico",
        )
