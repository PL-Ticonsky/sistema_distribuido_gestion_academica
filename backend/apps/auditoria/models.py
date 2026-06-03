from django.db import models

from apps.accounts.models import CustomUser


def schema_qualified_db_table(schema, table):
    return f'"{schema}"."{table}"'


class Auditoria(models.Model):
    id_auditoria = models.UUIDField(primary_key=True)
    usuario = models.ForeignKey(
        CustomUser,
        db_column="id_usuario",
        on_delete=models.DO_NOTHING,
        related_name="registros_auditoria",
    )
    esquema_afectado = models.CharField(max_length=80, blank=True, null=True)  # noqa: DJ001
    tabla_afectada = models.CharField(max_length=80, blank=True, null=True)  # noqa: DJ001
    accion_realizada = models.CharField(max_length=100)
    fecha_hora = models.DateTimeField()
    descripcion = models.CharField(max_length=255, blank=True, null=True)  # noqa: DJ001

    class Meta:
        managed = False
        db_table = schema_qualified_db_table("auditoria", "auditoria")
        ordering = ["-fecha_hora", "usuario__nombre"]
        verbose_name = "registro de auditoria"
        verbose_name_plural = "registros de auditoria"

    def __str__(self):
        return f"{self.usuario.nombre} - {self.accion_realizada}"
