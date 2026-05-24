from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from apps.auditoria.models import Auditoria


class AuditoriaListView(LoginRequiredMixin, ListView):
    model = Auditoria
    template_name = "auditoria/auditoria_list.html"
    context_object_name = "registros"

    def get_queryset(self):
        return Auditoria.objects.select_related("usuario").order_by(
            "-fecha_hora",
            "usuario__nombre",
        )


class AuditoriaDetailView(LoginRequiredMixin, DetailView):
    model = Auditoria
    template_name = "auditoria/auditoria_detail.html"
    context_object_name = "registro"
    pk_url_kwarg = "id_auditoria"

    def get_queryset(self):
        return Auditoria.objects.select_related("usuario")
