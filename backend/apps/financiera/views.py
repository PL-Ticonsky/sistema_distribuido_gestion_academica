from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView

from apps.accounts.access import FINANCIAL_ROLES, RoleRequiredMixin
from apps.financiera.models import MatriculaDetalle, Recibo, TarifaMatricula

READ_ONLY_MESSAGE = "La escritura financiera distribuida aun no esta habilitada."


class FinancialReadOnlyListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = FINANCIAL_ROLES
    paginate_by = 25
    filters = ()

    def get_queryset(self):
        queryset = super().get_queryset()
        for field in self.filters:
            value = self.request.GET.get(field)
            if value:
                queryset = queryset.filter(**{field: value})
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_filters"] = {
            field: self.request.GET.get(field, "") for field in self.filters
        }
        return context


class TarifaMatriculaListView(FinancialReadOnlyListView):
    model = TarifaMatricula
    template_name = "financiera/tarifa_list.html"
    context_object_name = "tarifas"
    filters = ("id_facultad", "programa_academico_id", "periodo_academico_id", "estado")

    def get_queryset(self):
        return super().get_queryset().select_related(
            "programa_academico",
            "programa_academico__facultad",
            "periodo_academico",
        )


class ReciboListView(FinancialReadOnlyListView):
    model = Recibo
    template_name = "financiera/recibo_list.html"
    context_object_name = "recibos"
    filters = ("id_facultad", "tarifa_matricula__periodo_academico_id", "estado_pago")

    def get_queryset(self):
        return super().get_queryset().select_related(
            "tarifa_matricula",
            "tarifa_matricula__programa_academico",
            "tarifa_matricula__periodo_academico",
        )


class MatriculaListView(FinancialReadOnlyListView):
    model = MatriculaDetalle
    template_name = "financiera/matricula_list.html"
    context_object_name = "matriculas"
    filters = (
        "id_facultad",
        "nombre_facultad",
        "id_programa_academico",
        "nombre_programa",
        "id_periodo_academico",
        "estado_pago",
        "estado_matricula",
    )


class ReadOnlyRedirectView(LoginRequiredMixin, View):
    redirect_url_name = "financiera:matricula_list"

    def get(self, request, *args, **kwargs):
        messages.warning(request, READ_ONLY_MESSAGE)
        return redirect(self.redirect_url_name)

    def post(self, request, *args, **kwargs):
        messages.warning(request, READ_ONLY_MESSAGE)
        return redirect(self.redirect_url_name)


class ReciboDetailView(ReadOnlyRedirectView):
    redirect_url_name = "financiera:recibo_list"


class MatriculaDetailView(ReadOnlyRedirectView):
    redirect_url_name = "financiera:matricula_list"


class TarifaMatriculaCreateView(ReadOnlyRedirectView):
    redirect_url_name = "financiera:tarifa_list"


class TarifaMatriculaUpdateView(ReadOnlyRedirectView):
    redirect_url_name = "financiera:tarifa_list"


class TarifaMatriculaToggleEstadoView(ReadOnlyRedirectView):
    redirect_url_name = "financiera:tarifa_list"


class ReciboCreateView(ReadOnlyRedirectView):
    redirect_url_name = "financiera:recibo_list"


class ReciboUpdateView(ReadOnlyRedirectView):
    redirect_url_name = "financiera:recibo_list"


class ReciboAnularView(ReadOnlyRedirectView):
    redirect_url_name = "financiera:recibo_list"


class MatriculaCreateView(ReadOnlyRedirectView):
    redirect_url_name = "financiera:matricula_list"


class MatriculaActivarView(ReadOnlyRedirectView):
    redirect_url_name = "financiera:matricula_list"


class MatriculaFinalizarView(ReadOnlyRedirectView):
    redirect_url_name = "financiera:matricula_list"


class MatriculaCancelarView(ReadOnlyRedirectView):
    redirect_url_name = "financiera:matricula_list"


class MatriculaAnularView(ReadOnlyRedirectView):
    redirect_url_name = "financiera:matricula_list"
