from django.db import models

from apps.academica.models import Estudiante
from apps.estructura.models import PeriodoAcademico, ProgramaAcademico


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
        db_table = "tarifa_matricula"
        ordering = [
            "periodo_academico",
            "programa_academico__nombre_programa",
        ]
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
    estudiante = models.ForeignKey(
        Estudiante,
        db_column="id_estudiante",
        on_delete=models.DO_NOTHING,
        related_name="recibos",
    )
    tarifa_matricula = models.ForeignKey(
        TarifaMatricula,
        db_column="id_tarifa_matricula",
        on_delete=models.DO_NOTHING,
        related_name="recibos",
    )
    fecha_pago = models.DateField(blank=True, null=True)
    valor_pagado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
    )
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
        db_table = "recibo"
        ordering = [
            "estudiante__usuario__nombre",
            "tarifa_matricula__periodo_academico",
        ]
        verbose_name = "recibo"
        verbose_name_plural = "recibos"

    def __str__(self):
        return f"{self.estudiante} - {self.tarifa_matricula}"


class Matricula(models.Model):
    class EstadoMatricula(models.TextChoices):
        PENDIENTE = "Pendiente", "Pendiente"
        ACTIVA = "Activa", "Activa"
        FINALIZADA = "Finalizada", "Finalizada"
        CANCELADA = "Cancelada", "Cancelada"
        ANULADA = "Anulada", "Anulada"

    id_matricula = models.UUIDField(primary_key=True)
    recibo = models.OneToOneField(
        Recibo,
        db_column="id_recibo",
        on_delete=models.DO_NOTHING,
        related_name="matricula",
    )
    estado_matricula = models.CharField(
        max_length=20,
        choices=EstadoMatricula.choices,
    )

    class Meta:
        managed = False
        db_table = "matricula"
        ordering = [
            "recibo__estudiante__usuario__nombre",
            "recibo__tarifa_matricula__periodo_academico",
        ]
        verbose_name = "matricula"
        verbose_name_plural = "matriculas"

    def __str__(self):
        return f"{self.recibo.estudiante} - {self.estado_matricula}"
