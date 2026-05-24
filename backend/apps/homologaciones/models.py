from django.db import models

from apps.academica.models import Estudiante, Profesor, ProgramaAsignatura


class Homologacion(models.Model):
    class EstadoHomologacion(models.TextChoices):
        SOLICITADA = "Solicitada", "Solicitada"
        EN_REVISION = "En revision", "En revision"
        APROBADA = "Aprobada", "Aprobada"
        RECHAZADA = "Rechazada", "Rechazada"
        CANCELADA = "Cancelada", "Cancelada"

    id_homologacion = models.UUIDField(primary_key=True)
    profesor_evaluador = models.ForeignKey(
        Profesor,
        db_column="id_profesor_evaluador",
        on_delete=models.DO_NOTHING,
        related_name="homologaciones_evaluadas",
    )
    estudiante = models.ForeignKey(
        Estudiante,
        db_column="id_estudiante",
        on_delete=models.DO_NOTHING,
        related_name="homologaciones",
    )
    asignatura_origen = models.CharField(max_length=100)
    institucion_origen = models.CharField(max_length=100)
    programa_asignatura = models.ForeignKey(
        ProgramaAsignatura,
        db_column="id_programa_asignatura",
        on_delete=models.DO_NOTHING,
        related_name="homologaciones",
    )
    fecha_solicitud = models.DateField()
    estado_homologacion = models.CharField(
        max_length=20,
        choices=EstadoHomologacion.choices,
    )
    observacion = models.CharField(max_length=255, blank=True, null=True)  # noqa: DJ001
    fecha_respuesta = models.DateField(blank=True, null=True)
    nota_obtenida = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "homologacion"
        ordering = [
            "estudiante__usuario__nombre",
            "-fecha_solicitud",
            "programa_asignatura__asignatura__nombre_asignatura",
        ]
        verbose_name = "homologacion"
        verbose_name_plural = "homologaciones"

    def __str__(self):
        return (
            f"{self.estudiante} - "
            f"{self.programa_asignatura.asignatura} - "
            f"{self.estado_homologacion}"
        )
