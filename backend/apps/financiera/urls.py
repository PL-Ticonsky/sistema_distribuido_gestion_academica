from django.urls import path

from apps.financiera.views import (
    MatriculaDetailView,
    MatriculaListView,
    ReciboDetailView,
    ReciboListView,
    TarifaMatriculaListView,
)

app_name = "financiera"

urlpatterns = [
    path("tarifas/", TarifaMatriculaListView.as_view(), name="tarifa_list"),
    path("recibos/", ReciboListView.as_view(), name="recibo_list"),
    path("recibos/<uuid:id_recibo>/", ReciboDetailView.as_view(), name="recibo_detail"),
    path("matriculas/", MatriculaListView.as_view(), name="matricula_list"),
    path(
        "matriculas/<uuid:id_matricula>/",
        MatriculaDetailView.as_view(),
        name="matricula_detail",
    ),
]
