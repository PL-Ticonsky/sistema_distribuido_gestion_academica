from django.db import models


class Facultad(models.Model):
    id_facultad = models.CharField(max_length=10, primary_key=True)
    nombre_facultad = models.CharField(max_length=80)
    ubicacion = models.CharField(max_length=80, blank=True, null=True)  # noqa: DJ001
    correo_institucional = models.EmailField(
        max_length=120,
        unique=True,
        blank=True,
        null=True,
    )  # noqa: DJ001

    class Meta:
        managed = False
        db_table = "facultad"
        ordering = ["nombre_facultad"]
        verbose_name = "facultad"
        verbose_name_plural = "facultades"

    def __str__(self):
        return self.nombre_facultad


class ProgramaAcademico(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "Activo", "Activo"
        INACTIVO = "Inactivo", "Inactivo"

    class Modalidad(models.TextChoices):
        PRESENCIAL = "Presencial", "Presencial"
        VIRTUAL = "Virtual", "Virtual"
        HIBRIDA = "Hibrida", "Hibrida"

    class NivelFormacion(models.TextChoices):
        TECNICO = "Tecnico", "Tecnico"
        TECNOLOGICO = "Tecnologico", "Tecnologico"
        PREGRADO = "Pregrado", "Pregrado"
        ESPECIALIZACION = "Especializacion", "Especializacion"
        MAESTRIA = "Maestria", "Maestria"
        DOCTORADO = "Doctorado", "Doctorado"

    id_programa_academico = models.CharField(max_length=20, primary_key=True)
    facultad = models.ForeignKey(
        Facultad,
        db_column="id_facultad",
        on_delete=models.DO_NOTHING,
        related_name="programas",
    )
    nombre_programa = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=Estado.choices)
    modalidad = models.CharField(max_length=20, choices=Modalidad.choices)
    nivel_formacion = models.CharField(max_length=30, choices=NivelFormacion.choices)

    class Meta:
        managed = False
        db_table = "programa_academico"
        ordering = ["nombre_programa"]
        verbose_name = "programa academico"
        verbose_name_plural = "programas academicos"

    def __str__(self):
        return self.nombre_programa


class PeriodoAcademico(models.Model):
    class Estado(models.TextChoices):
        PLANEADO = "Planeado", "Planeado"
        ACTIVO = "Activo", "Activo"
        FINALIZADO = "Finalizado", "Finalizado"
        CANCELADO = "Cancelado", "Cancelado"

    id_periodo_academico = models.CharField(max_length=10, primary_key=True)
    fecha_inicio = models.DateField()
    fecha_final = models.DateField()
    estado = models.CharField(max_length=20, choices=Estado.choices)

    class Meta:
        managed = False
        db_table = "periodo_academico"
        ordering = ["-fecha_inicio", "id_periodo_academico"]
        verbose_name = "periodo academico"
        verbose_name_plural = "periodos academicos"

    def __str__(self):
        return self.id_periodo_academico
