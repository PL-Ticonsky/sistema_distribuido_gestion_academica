from django.urls import path

from apps.financiera.views import (
    MatriculaActivarView,
    MatriculaAnularView,
    MatriculaCancelarView,
    MatriculaCreateView,
    MatriculaDetailView,
    MatriculaFinalizarView,
    MatriculaListView,
    ReciboAnularView,
    ReciboCreateView,
    ReciboDetailView,
    ReciboListView,
    ReciboUpdateView,
    TarifaMatriculaCreateView,
    TarifaMatriculaListView,
    TarifaMatriculaToggleEstadoView,
    TarifaMatriculaUpdateView,
)

app_name = "financiera"

urlpatterns = [
    path("tarifas/", TarifaMatriculaListView.as_view(), name="tarifa_list"),
    path("tarifas/crear/", TarifaMatriculaCreateView.as_view(), name="tarifa_create"),
    path(
        "tarifas/<uuid:id_tarifa_matricula>/editar/",
        TarifaMatriculaUpdateView.as_view(),
        name="tarifa_update",
    ),
    path(
        "tarifas/<uuid:id_tarifa_matricula>/cambiar-estado/",
        TarifaMatriculaToggleEstadoView.as_view(),
        name="tarifa_toggle_estado",
    ),
    path("recibos/", ReciboListView.as_view(), name="recibo_list"),
    path("recibos/crear/", ReciboCreateView.as_view(), name="recibo_create"),
    path("recibos/<uuid:id_recibo>/", ReciboDetailView.as_view(), name="recibo_detail"),
    path(
        "recibos/<uuid:id_recibo>/editar/",
        ReciboUpdateView.as_view(),
        name="recibo_update",
    ),
    path(
        "recibos/<uuid:id_recibo>/anular/",
        ReciboAnularView.as_view(),
        name="recibo_anular",
    ),
    path("matriculas/", MatriculaListView.as_view(), name="matricula_list"),
    path(
        "matriculas/crear/",
        MatriculaCreateView.as_view(),
        name="matricula_create",
    ),
    path(
        "matriculas/<uuid:id_matricula>/",
        MatriculaDetailView.as_view(),
        name="matricula_detail",
    ),
    path(
        "matriculas/<uuid:id_matricula>/activar/",
        MatriculaActivarView.as_view(),
        name="matricula_activar",
    ),
    path(
        "matriculas/<uuid:id_matricula>/finalizar/",
        MatriculaFinalizarView.as_view(),
        name="matricula_finalizar",
    ),
    path(
        "matriculas/<uuid:id_matricula>/cancelar/",
        MatriculaCancelarView.as_view(),
        name="matricula_cancelar",
    ),
    path(
        "matriculas/<uuid:id_matricula>/anular/",
        MatriculaAnularView.as_view(),
        name="matricula_anular",
    ),
]
