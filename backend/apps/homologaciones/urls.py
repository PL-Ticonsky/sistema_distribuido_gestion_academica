from django.urls import path

from apps.homologaciones.views import (
    HomologacionAssignEvaluatorView,
    HomologacionCancelView,
    HomologacionCreateView,
    HomologacionDetailView,
    HomologacionEvaluateView,
    HomologacionListView,
)

app_name = "homologaciones"

urlpatterns = [
    path("", HomologacionListView.as_view(), name="homologacion_list"),
    path("crear/", HomologacionCreateView.as_view(), name="homologacion_create"),
    path(
        "<uuid:id_homologacion>/",
        HomologacionDetailView.as_view(),
        name="homologacion_detail",
    ),
    path(
        "<uuid:id_homologacion>/asignar-evaluador/",
        HomologacionAssignEvaluatorView.as_view(),
        name="homologacion_assign_evaluator",
    ),
    path(
        "<uuid:id_homologacion>/evaluar/",
        HomologacionEvaluateView.as_view(),
        name="homologacion_evaluate",
    ),
    path(
        "<uuid:id_homologacion>/cancelar/",
        HomologacionCancelView.as_view(),
        name="homologacion_cancel",
    ),
]
