from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from apps.estructura.models import Facultad, PeriodoAcademico, ProgramaAcademico


class FacultadListView(LoginRequiredMixin, ListView):
    model = Facultad
    template_name = "estructura/facultad_list.html"
    context_object_name = "facultades"


class FacultadDetailView(LoginRequiredMixin, DetailView):
    model = Facultad
    template_name = "estructura/facultad_detail.html"
    context_object_name = "facultad"
    pk_url_kwarg = "id_facultad"

    def get_queryset(self):
        return Facultad.objects.prefetch_related("programas")


class ProgramaListView(LoginRequiredMixin, ListView):
    model = ProgramaAcademico
    template_name = "estructura/programa_list.html"
    context_object_name = "programas"

    def get_queryset(self):
        return ProgramaAcademico.objects.select_related("facultad")


class PeriodoAcademicoListView(LoginRequiredMixin, ListView):
    model = PeriodoAcademico
    template_name = "estructura/periodo_list.html"
    context_object_name = "periodos"
