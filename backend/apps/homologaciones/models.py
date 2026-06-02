from django.db import models


def schema_qualified_db_table(schema, table):
    return f'"{schema}"."{table}"'


class HomologacionGlobal(models.Model):
    class EstadoHomologacion(models.TextChoices):
        SOLICITADA = "Solicitada", "Solicitada"
        EN_REVISION = "En revision", "En revision"
        APROBADA = "Aprobada", "Aprobada"
        RECHAZADA = "Rechazada", "Rechazada"
        CANCELADA = "Cancelada", "Cancelada"

    nodo_origen = models.TextField(blank=True, null=True)  # noqa: DJ001
    id_homologacion = models.UUIDField(primary_key=True)
    id_facultad = models.CharField(max_length=10, blank=True, null=True)  # noqa: DJ001
    id_profesor_evaluador = models.UUIDField(blank=True, null=True)  # noqa: DJ001
    id_estudiante = models.UUIDField(blank=True, null=True)  # noqa: DJ001
    asignatura_origen = models.CharField(max_length=120, blank=True, null=True)  # noqa: DJ001
    institucion_origen = models.CharField(max_length=120, blank=True, null=True)  # noqa: DJ001
    id_programa_asignatura = models.UUIDField(blank=True, null=True)  # noqa: DJ001
    fecha_solicitud = models.DateField(blank=True, null=True)  # noqa: DJ001
    estado_homologacion = models.CharField(  # noqa: DJ001
        max_length=20,
        choices=EstadoHomologacion.choices,
        blank=True,
        null=True,
    )
    observacion = models.CharField(max_length=255, blank=True, null=True)  # noqa: DJ001
    fecha_respuesta = models.DateField(blank=True, null=True)  # noqa: DJ001
    nota_obtenida = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
    )  # noqa: DJ001

    class Meta:
        managed = False
        db_table = schema_qualified_db_table("reportes", "vw_homologaciones_global")
        ordering = ["-fecha_solicitud", "id_homologacion"]
        verbose_name = "homologacion global"
        verbose_name_plural = "homologaciones globales"

    def __str__(self):
        return f"{self.asignatura_origen} - {self.estado_homologacion}"


Homologacion = HomologacionGlobal
