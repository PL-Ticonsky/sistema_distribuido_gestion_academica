from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.views.generic import DetailView, ListView

from apps.accounts.access import HOMOLOGATION_ROLES, RoleRequiredMixin
from apps.homologaciones.models import HomologacionGlobal

READ_ONLY_MESSAGE = "La escritura de homologaciones distribuida aun no esta habilitada."


class HomologacionListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = HOMOLOGATION_ROLES
    model = HomologacionGlobal
    template_name = "homologaciones/homologacion_list.html"
    context_object_name = "homologaciones"
    paginate_by = 25
    filters = (
        "id_facultad",
        "estado_homologacion",
        "fecha_solicitud",
        "id_estudiante",
        "id_profesor_evaluador",
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        forced_state = getattr(self, "forced_state", None)
        if forced_state:
            queryset = queryset.filter(estado_homologacion=forced_state)
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


class HomologacionSolicitudesListView(HomologacionListView):
    forced_state = "Solicitada"


class HomologacionPendientesListView(HomologacionListView):
    forced_state = "En revision"


class HomologacionDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    allowed_roles = HOMOLOGATION_ROLES
    model = HomologacionGlobal
    template_name = "homologaciones/homologacion_detail.html"
    context_object_name = "homologacion"
    pk_url_kwarg = "id_homologacion"


class ReadOnlyRedirectView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        messages.warning(request, READ_ONLY_MESSAGE)
        return redirect("homologaciones:homologacion_list")

    def post(self, request, *args, **kwargs):
        messages.warning(request, READ_ONLY_MESSAGE)
        return redirect("homologaciones:homologacion_list")


class HomologacionCreateView(ReadOnlyRedirectView):
    pass


class HomologacionAssignEvaluatorView(ReadOnlyRedirectView):
    pass


class HomologacionEvaluateView(ReadOnlyRedirectView):
    pass


class HomologacionCancelView(ReadOnlyRedirectView):
    pass
