from django.db import models

from apps.accounts.models import CustomUser
from apps.estructura.models import Facultad, PeriodoAcademico, ProgramaAcademico


class Asignatura(models.Model):
    class Estado(models.TextChoices):
        ACTIVA = "Activa", "Activa"
        INACTIVA = "Inactiva", "Inactiva"

    cod_asignatura = models.CharField(max_length=20, primary_key=True)
    nombre_asignatura = models.CharField(max_length=100)
    creditos = models.IntegerField()
    estado = models.CharField(max_length=20, choices=Estado.choices)
    horas_teoria = models.IntegerField()
    horas_pract = models.IntegerField()
    homologable = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "asignatura"
        ordering = ["nombre_asignatura"]
        verbose_name = "asignatura"
        verbose_name_plural = "asignaturas"

    def __str__(self):
        return self.nombre_asignatura


class ProgramaAsignatura(models.Model):
    class TipoAsignatura(models.TextChoices):
        OBLIGATORIA = "Obligatoria", "Obligatoria"
        ELECTIVA = "Electiva", "Electiva"

    class Estado(models.TextChoices):
        ACTIVA = "Activa", "Activa"
        INACTIVA = "Inactiva", "Inactiva"

    id_programa_asignatura = models.UUIDField(primary_key=True)
    programa_academico = models.ForeignKey(
        ProgramaAcademico,
        db_column="id_programa_academico",
        on_delete=models.DO_NOTHING,
        related_name="plan_asignaturas",
    )
    asignatura = models.ForeignKey(
        Asignatura,
        db_column="cod_asignatura",
        on_delete=models.DO_NOTHING,
        related_name="programas",
    )
    semestre_sugerido = models.IntegerField()
    tipo_asignatura = models.CharField(max_length=20, choices=TipoAsignatura.choices)
    estado = models.CharField(max_length=20, choices=Estado.choices)

    class Meta:
        managed = False
        db_table = "programa_asignatura"
        ordering = ["programa_academico", "semestre_sugerido", "asignatura"]
        verbose_name = "asignatura por programa"
        verbose_name_plural = "asignaturas por programa"

    def __str__(self):
        return f"{self.programa_academico} - {self.asignatura}"


class PreRequisito(models.Model):
    id_pre_requisito = models.UUIDField(primary_key=True)
    programa_academico = models.ForeignKey(
        ProgramaAcademico,
        db_column="id_programa_academico",
        on_delete=models.DO_NOTHING,
        related_name="pre_requisitos",
    )
    programa_asignatura = models.ForeignKey(
        ProgramaAsignatura,
        db_column="id_programa_asignatura",
        on_delete=models.DO_NOTHING,
        related_name="pre_requisitos",
    )
    programa_asignatura_requisito = models.ForeignKey(
        ProgramaAsignatura,
        db_column="id_programa_asignatura_requisito",
        on_delete=models.DO_NOTHING,
        related_name="asignaturas_dependientes",
    )

    class Meta:
        managed = False
        db_table = "pre_requisito"
        ordering = ["programa_academico", "programa_asignatura"]
        verbose_name = "pre requisito"
        verbose_name_plural = "pre requisitos"

    def __str__(self):
        return (
            f"{self.programa_asignatura.asignatura} requiere "
            f"{self.programa_asignatura_requisito.asignatura}"
        )


class Estudiante(models.Model):
    id_estudiante = models.UUIDField(primary_key=True)
    usuario = models.ForeignKey(
        CustomUser,
        db_column="id_usuario",
        on_delete=models.DO_NOTHING,
        related_name="estudiantes_academica",
    )
    programa_academico = models.ForeignKey(
        ProgramaAcademico,
        db_column="id_programa_academico",
        on_delete=models.DO_NOTHING,
        related_name="estudiantes_academica",
    )
    limite_matriculas = models.IntegerField()
    estado_estudiante = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = "estudiante"
        ordering = ["usuario__nombre"]
        verbose_name = "estudiante"
        verbose_name_plural = "estudiantes"

    def __str__(self):
        return self.usuario.nombre


class Profesor(models.Model):
    id_profesor = models.UUIDField(primary_key=True)
    usuario = models.ForeignKey(
        CustomUser,
        db_column="id_usuario",
        on_delete=models.DO_NOTHING,
        related_name="profesores_academica",
    )
    facultad = models.ForeignKey(
        Facultad,
        db_column="id_facultad",
        on_delete=models.DO_NOTHING,
        related_name="profesores_academica",
    )
    categoria = models.CharField(max_length=20, blank=True, null=True)  # noqa: DJ001
    vinculacion = models.CharField(max_length=20, blank=True, null=True)  # noqa: DJ001

    class Meta:
        managed = False
        db_table = "profesor"
        ordering = ["usuario__nombre"]
        verbose_name = "profesor"
        verbose_name_plural = "profesores"

    def __str__(self):
        return self.usuario.nombre


class Decano(models.Model):
    id_decano = models.UUIDField(primary_key=True)
    profesor = models.ForeignKey(
        Profesor,
        db_column="id_profesor",
        on_delete=models.DO_NOTHING,
        related_name="decanaturas",
    )
    periodo_academico = models.ForeignKey(
        PeriodoAcademico,
        db_column="id_periodo_academico",
        on_delete=models.DO_NOTHING,
        related_name="decanaturas",
    )
    facultad = models.ForeignKey(
        Facultad,
        db_column="id_facultad",
        on_delete=models.DO_NOTHING,
        related_name="decanaturas",
    )

    class Meta:
        managed = False
        db_table = "decano"
        ordering = ["periodo_academico", "facultad"]
        verbose_name = "decano"
        verbose_name_plural = "decanos"

    def __str__(self):
        return f"{self.profesor} - {self.facultad} - {self.periodo_academico}"


class Coordinador(models.Model):
    id_coordinador = models.UUIDField(primary_key=True)
    profesor = models.ForeignKey(
        Profesor,
        db_column="id_profesor",
        on_delete=models.DO_NOTHING,
        related_name="coordinaciones",
    )
    periodo_academico = models.ForeignKey(
        PeriodoAcademico,
        db_column="id_periodo_academico",
        on_delete=models.DO_NOTHING,
        related_name="coordinaciones",
    )
    programa_academico = models.ForeignKey(
        ProgramaAcademico,
        db_column="id_programa_academico",
        on_delete=models.DO_NOTHING,
        related_name="coordinaciones",
    )

    class Meta:
        managed = False
        db_table = "coordinador"
        ordering = ["periodo_academico", "programa_academico"]
        verbose_name = "coordinador"
        verbose_name_plural = "coordinadores"

    def __str__(self):
        return f"{self.profesor} - {self.programa_academico} - {self.periodo_academico}"


class Grupo(models.Model):
    class EstadoGrupo(models.TextChoices):
        ABIERTO = "Abierto", "Abierto"
        EN_CURSO = "En curso", "En curso"
        FINALIZADO = "Finalizado", "Finalizado"
        CANCELADO = "Cancelado", "Cancelado"

    id_grupo = models.UUIDField(primary_key=True)
    programa_asignatura = models.ForeignKey(
        ProgramaAsignatura,
        db_column="id_programa_asignatura",
        on_delete=models.DO_NOTHING,
        related_name="grupos",
    )
    periodo_academico = models.ForeignKey(
        PeriodoAcademico,
        db_column="id_periodo_academico",
        on_delete=models.DO_NOTHING,
        related_name="grupos",
    )
    profesor = models.ForeignKey(
        Profesor,
        db_column="id_profesor",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="grupos",
    )
    codigo_grupo = models.CharField(max_length=20)
    cupo_maximo = models.IntegerField()
    estado_grupo = models.CharField(max_length=20, choices=EstadoGrupo.choices)

    class Meta:
        managed = False
        db_table = "grupo"
        ordering = ["periodo_academico", "programa_asignatura", "codigo_grupo"]
        verbose_name = "grupo"
        verbose_name_plural = "grupos"

    def __str__(self):
        return f"{self.programa_asignatura.asignatura} - {self.codigo_grupo}"


class Inscripcion(models.Model):
    class EstadoInscripcion(models.TextChoices):
        CURSANDO = "Cursando", "Cursando"
        APROBADA = "Aprobada", "Aprobada"
        REPROBADA = "Reprobada", "Reprobada"
        CANCELADA = "Cancelada", "Cancelada"

    id_inscripcion = models.UUIDField(primary_key=True)
    grupo = models.ForeignKey(
        Grupo,
        db_column="id_grupo",
        on_delete=models.DO_NOTHING,
        related_name="inscripciones",
    )
    estudiante = models.ForeignKey(
        Estudiante,
        db_column="id_estudiante",
        on_delete=models.DO_NOTHING,
        related_name="inscripciones",
    )
    nota1 = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    nota2 = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    nota3 = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    nota_final = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
    )
    intento = models.IntegerField()
    estado_inscripcion = models.CharField(
        max_length=20,
        choices=EstadoInscripcion.choices,
    )

    class Meta:
        managed = False
        db_table = "inscripcion"
        ordering = ["grupo", "estudiante"]
        verbose_name = "inscripcion"
        verbose_name_plural = "inscripciones"

    def __str__(self):
        return f"{self.estudiante} - {self.grupo}"
