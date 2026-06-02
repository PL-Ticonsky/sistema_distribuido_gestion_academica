from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("", include("apps.accounts.urls")),
    path(
        "accounts/login/",
        RedirectView.as_view(pattern_name="accounts:login", permanent=False),
    ),
    path("academica/", include("apps.academica.urls")),
    path("auditoria/", include("apps.auditoria.urls")),
    path("estructura/", include("apps.estructura.urls")),
    path("financiera/", include("apps.financiera.urls")),
    path("homologaciones/", include("apps.homologaciones.urls")),
    path("indicadores/", include("apps.indicadores.urls")),
    path("reportes/", include("apps.reportes.urls")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
