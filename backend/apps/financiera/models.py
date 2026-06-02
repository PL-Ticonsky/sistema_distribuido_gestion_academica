from django.db import models

from apps.estructura.models import PeriodoAcademico, ProgramaAcademico


def schema_qualified_db_table(schema, table):
    return f'"{schema}"."{table}"'


class TarifaMatricula(models.Model):
    class Estado(models.TextChoices):
        ACTIVA = "Activa", "Activa"
        INACTIVA = "Inactiva", "Inactiva"

    id_tarifa_matricula = models.UUIDField(primary_key=True)
    programa_academico = models.ForeignKey(
        ProgramaAcademico,
        db_column="id_programa_academico",
        on_delete=models.DO_NOTHING,
        related_name="tarifas_matricula",
    )
    id_facultad = models.CharField(max_length=10)
    periodo_academico = models.ForeignKey(
        PeriodoAcademico,
        db_column="id_periodo_academico",
        on_delete=models.DO_NOTHING,
        related_name="tarifas_matricula",
    )
    valor_matricula = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_limite_ordinaria = models.DateField()
    fecha_limite_extraordinaria = models.DateField()
    estado = models.CharField(max_length=20, choices=Estado.choices)

    class Meta:
        managed = False
        db_table = schema_qualified_db_table("financiero", "tarifa_matricula")
        ordering = ["periodo_academico_id", "programa_academico_id"]
        verbose_name = "tarifa de matricula"
        verbose_name_plural = "tarifas de matricula"

    def __str__(self):
        return f"{self.programa_academico} - {self.periodo_academico}"


class Recibo(models.Model):
    class MetodoPago(models.TextChoices):
        EFECTIVO = "Efectivo", "Efectivo"
        TARJETA = "Tarjeta", "Tarjeta"
        PSE = "PSE", "PSE"
        TRANSFERENCIA = "Transferencia", "Transferencia"
        CONSIGNACION = "Consignacion", "Consignacion"

    class EstadoPago(models.TextChoices):
        PENDIENTE = "Pendiente", "Pendiente"
        PAGADO = "Pagado", "Pagado"
        VENCIDO = "Vencido", "Vencido"
        ANULADO = "Anulado", "Anulado"

    id_recibo = models.UUIDField(primary_key=True)
    id_estudiante = models.UUIDField()
    id_facultad = models.CharField(max_length=10)
    tarifa_matricula = models.ForeignKey(
        TarifaMatricula,
        db_column="id_tarifa_matricula",
        on_delete=models.DO_NOTHING,
        related_name="recibos",
    )
    fecha_pago = models.DateField(blank=True, null=True)  # noqa: DJ001
    valor_pagado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
    )  # noqa: DJ001
    metodo_pago = models.CharField(  # noqa: DJ001
        max_length=20,
        choices=MetodoPago.choices,
        blank=True,
        null=True,
    )
    estado_pago = models.CharField(max_length=20, choices=EstadoPago.choices)
    extras = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        managed = False
        db_table = schema_qualified_db_table("financiero", "recibo")
        ordering = ["tarifa_matricula_id", "id_estudiante"]
        verbose_name = "recibo"
        verbose_name_plural = "recibos"

    def __str__(self):
        return f"{self.id_estudiante} - {self.tarifa_matricula}"


class MatriculaDetalle(models.Model):
    nodo_origen = models.TextField(blank=True, null=True)  # noqa: DJ001
    id_matricula = models.UUIDField(primary_key=True)
    id_facultad = models.CharField(max_length=10, blank=True, null=True)  # noqa: DJ001
    nombre_facultad = models.CharField(max_length=80, blank=True, null=True)  # noqa: DJ001
    id_estudiante = models.UUIDField(blank=True, null=True)  # noqa: DJ001
    estudiante = models.CharField(max_length=160, blank=True, null=True)  # noqa: DJ001
    id_programa_academico = models.CharField(max_length=20, blank=True, null=True)  # noqa: DJ001
    nombre_programa = models.CharField(max_length=100, blank=True, null=True)  # noqa: DJ001
    id_periodo_academico = models.CharField(max_length=10, blank=True, null=True)  # noqa: DJ001
    estado_matricula = models.CharField(max_length=20, blank=True, null=True)  # noqa: DJ001
    estado_pago = models.CharField(max_length=20, blank=True, null=True)  # noqa: DJ001
    valor_pagado = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        blank=True,
        null=True,
    )  # noqa: DJ001
    fecha_pago = models.DateField(blank=True, null=True)  # noqa: DJ001
    id_recibo = models.UUIDField(blank=True, null=True)  # noqa: DJ001

    class Meta:
        managed = False
        db_table = schema_qualified_db_table("reportes", "vw_matriculas_detalle")
        ordering = ["nombre_facultad", "estudiante", "id_periodo_academico"]
        verbose_name = "detalle de matricula"
        verbose_name_plural = "detalles de matricula"

    def __str__(self):
        return f"{self.estudiante} - {self.id_periodo_academico}"


Matricula = MatriculaDetalle
