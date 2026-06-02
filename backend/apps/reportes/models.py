from django.db import models


class FacultadCentral(models.Model):
    id_facultad = models.CharField(max_length=10, primary_key=True)
    nombre_facultad = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=100, blank=True, null=True)  # noqa: DJ001
    correo_institucional = models.EmailField(  # noqa: DJ001
        max_length=120,
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = '"institucional"."facultad"'
        ordering = ["nombre_facultad"]
        verbose_name = "facultad central"
        verbose_name_plural = "facultades centrales"

    def __str__(self):
        return self.nombre_facultad


class ProgramaAcademicoCentral(models.Model):
    id_programa_academico = models.CharField(max_length=20, primary_key=True)
    id_facultad = models.CharField(max_length=10)
    nombre_programa = models.CharField(max_length=120)
    estado = models.CharField(max_length=20)
    modalidad = models.CharField(max_length=20)
    nivel_formacion = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = '"institucional"."programa_academico"'
        ordering = ["nombre_programa"]
        verbose_name = "programa academico central"
        verbose_name_plural = "programas academicos centrales"

    def __str__(self):
        return self.nombre_programa


class PeriodoAcademicoCentral(models.Model):
    id_periodo_academico = models.CharField(max_length=10, primary_key=True)
    fecha_inicio = models.DateField()
    fecha_final = models.DateField()
    estado = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = '"institucional"."periodo_academico"'
        ordering = ["-fecha_inicio", "id_periodo_academico"]
        verbose_name = "periodo academico central"
        verbose_name_plural = "periodos academicos centrales"

    def __str__(self):
        return self.id_periodo_academico


class AsignaturaCentral(models.Model):
    cod_asignatura = models.CharField(max_length=20, primary_key=True)
    nombre_asignatura = models.CharField(max_length=120)
    creditos = models.IntegerField()
    estado = models.CharField(max_length=20)
    horas_teoria = models.IntegerField()
    horas_pract = models.IntegerField()
    homologable = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = '"institucional"."asignatura"'
        ordering = ["nombre_asignatura"]
        verbose_name = "asignatura central"
        verbose_name_plural = "asignaturas centrales"

    def __str__(self):
        return self.nombre_asignatura


class UsuarioGlobal(models.Model):
    id_usuario = models.UUIDField(primary_key=True)
    nombre = models.CharField(max_length=100)
    tipo_de_documento = models.CharField(max_length=2)
    numero_de_documento = models.CharField(max_length=20)
    correo = models.EmailField(max_length=120)
    direccion = models.CharField(max_length=120, blank=True, null=True)  # noqa: DJ001
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = '"reportes"."vw_usuarios_global"'
        ordering = ["nombre"]
        verbose_name = "usuario global"
        verbose_name_plural = "usuarios globales"

    def __str__(self):
        return self.nombre


class EstudianteDetalle(models.Model):
    nodo_origen = models.CharField(max_length=80, blank=True, null=True)  # noqa: DJ001
    id_estudiante = models.UUIDField(primary_key=True)
    id_usuario = models.UUIDField()
    id_facultad = models.CharField(max_length=10)
    nombre_facultad = models.CharField(max_length=100, blank=True, null=True)  # noqa: DJ001
    id_programa_academico = models.CharField(max_length=20)
    nombre_programa = models.CharField(max_length=120, blank=True, null=True)  # noqa: DJ001
    estudiante = models.CharField(max_length=100, blank=True, null=True)  # noqa: DJ001
    correo = models.EmailField(max_length=120, blank=True, null=True)  # noqa: DJ001
    estado_estudiante = models.CharField(max_length=20, blank=True, null=True)  # noqa: DJ001
    limite_matriculas = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"reportes"."vw_estudiantes_detalle"'
        ordering = ["nombre_facultad", "nombre_programa", "estudiante"]
        verbose_name = "estudiante global"
        verbose_name_plural = "estudiantes globales"

    def __str__(self):
        return self.estudiante or str(self.id_estudiante)


class ProfesorDetalle(models.Model):
    nodo_origen = models.CharField(max_length=80, blank=True, null=True)  # noqa: DJ001
    id_profesor = models.UUIDField(primary_key=True)
    id_usuario = models.UUIDField()
    id_facultad = models.CharField(max_length=10)
    nombre_facultad = models.CharField(max_length=100, blank=True, null=True)  # noqa: DJ001
    profesor = models.CharField(max_length=100, blank=True, null=True)  # noqa: DJ001
    correo = models.EmailField(max_length=120, blank=True, null=True)  # noqa: DJ001
    categoria = models.CharField(max_length=20, blank=True, null=True)  # noqa: DJ001
    vinculacion = models.CharField(max_length=20, blank=True, null=True)  # noqa: DJ001

    class Meta:
        managed = False
        db_table = '"reportes"."vw_profesores_detalle"'
        ordering = ["nombre_facultad", "profesor"]
        verbose_name = "profesor global"
        verbose_name_plural = "profesores globales"

    def __str__(self):
        return self.profesor or str(self.id_profesor)


class GrupoDetalle(models.Model):
    nodo_origen = models.CharField(max_length=80, blank=True, null=True)  # noqa: DJ001
    id_grupo = models.UUIDField(primary_key=True)
    id_facultad = models.CharField(max_length=10)
    nombre_facultad = models.CharField(max_length=100, blank=True, null=True)  # noqa: DJ001
    id_periodo_academico = models.CharField(max_length=10)
    id_programa_academico = models.CharField(max_length=20)
    nombre_programa = models.CharField(max_length=120, blank=True, null=True)  # noqa: DJ001
    id_programa_asignatura = models.UUIDField()
    cod_asignatura = models.CharField(max_length=20)
    nombre_asignatura = models.CharField(max_length=120, blank=True, null=True)  # noqa: DJ001
    creditos = models.IntegerField(blank=True, null=True)
    codigo_grupo = models.CharField(max_length=20)
    estado_grupo = models.CharField(max_length=20)
    cupo_maximo = models.IntegerField()
    id_profesor = models.UUIDField(blank=True, null=True)
    profesor = models.CharField(max_length=100, blank=True, null=True)  # noqa: DJ001

    class Meta:
        managed = False
        db_table = '"reportes"."vw_grupos_detalle"'
        ordering = [
            "nombre_facultad",
            "id_periodo_academico",
            "nombre_programa",
            "nombre_asignatura",
            "codigo_grupo",
        ]
        verbose_name = "grupo global"
        verbose_name_plural = "grupos globales"

    def __str__(self):
        return f"{self.nombre_asignatura or self.cod_asignatura} - {self.codigo_grupo}"


class InscripcionDetalle(models.Model):
    nodo_origen = models.CharField(max_length=80, blank=True, null=True)  # noqa: DJ001
    id_inscripcion = models.UUIDField(primary_key=True)
    id_facultad = models.CharField(max_length=10)
    nombre_facultad = models.CharField(max_length=100, blank=True, null=True)  # noqa: DJ001
    id_estudiante = models.UUIDField()
    estudiante = models.CharField(max_length=100, blank=True, null=True)  # noqa: DJ001
    id_programa_academico = models.CharField(max_length=20)
    nombre_programa = models.CharField(max_length=120, blank=True, null=True)  # noqa: DJ001
    id_periodo_academico = models.CharField(max_length=10)
    cod_asignatura = models.CharField(max_length=20)
    nombre_asignatura = models.CharField(max_length=120, blank=True, null=True)  # noqa: DJ001
    creditos = models.IntegerField(blank=True, null=True)
    id_grupo = models.UUIDField()
    codigo_grupo = models.CharField(max_length=20)
    id_profesor = models.UUIDField(blank=True, null=True)
    profesor = models.CharField(max_length=100, blank=True, null=True)  # noqa: DJ001
    nota_final = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
    )
    intento = models.IntegerField()
    estado_inscripcion = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = '"reportes"."vw_inscripciones_detalle"'
        ordering = [
            "nombre_facultad",
            "id_periodo_academico",
            "nombre_programa",
            "estudiante",
        ]
        verbose_name = "inscripcion global"
        verbose_name_plural = "inscripciones globales"

    def __str__(self):
        estudiante = self.estudiante or self.id_estudiante
        asignatura = self.nombre_asignatura or self.cod_asignatura
        return f"{estudiante} - {asignatura}"


class MatriculaDetalle(models.Model):
    nodo_origen = models.CharField(max_length=80, blank=True, null=True)  # noqa: DJ001
    id_matricula = models.UUIDField(primary_key=True)
    id_facultad = models.CharField(max_length=10)
    nombre_facultad = models.CharField(max_length=100, blank=True, null=True)  # noqa: DJ001
    id_estudiante = models.UUIDField()
    estudiante = models.CharField(max_length=100, blank=True, null=True)  # noqa: DJ001
    id_programa_academico = models.CharField(max_length=20)
    nombre_programa = models.CharField(max_length=120, blank=True, null=True)  # noqa: DJ001
    id_periodo_academico = models.CharField(max_length=10)
    estado_matricula = models.CharField(max_length=20)
    estado_pago = models.CharField(max_length=20, blank=True, null=True)  # noqa: DJ001
    valor_pagado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
    )
    fecha_pago = models.DateField(blank=True, null=True)
    id_recibo = models.UUIDField()

    class Meta:
        managed = False
        db_table = '"reportes"."vw_matriculas_detalle"'
        ordering = [
            "nombre_facultad",
            "id_periodo_academico",
            "nombre_programa",
            "estudiante",
        ]
        verbose_name = "matricula global"
        verbose_name_plural = "matriculas globales"

    def __str__(self):
        return f"{self.estudiante or self.id_estudiante} - {self.id_periodo_academico}"


class HomologacionGlobal(models.Model):
    nodo_origen = models.CharField(max_length=80, blank=True, null=True)  # noqa: DJ001
    id_homologacion = models.UUIDField(primary_key=True)
    id_facultad = models.CharField(max_length=10)
    id_profesor_evaluador = models.UUIDField()
    id_estudiante = models.UUIDField()
    asignatura_origen = models.CharField(max_length=100)
    institucion_origen = models.CharField(max_length=100)
    id_programa_asignatura = models.UUIDField()
    fecha_solicitud = models.DateField()
    estado_homologacion = models.CharField(max_length=20)
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
        db_table = '"reportes"."vw_homologaciones_global"'
        ordering = ["id_facultad", "-fecha_solicitud", "estado_homologacion"]
        verbose_name = "homologacion global"
        verbose_name_plural = "homologaciones globales"

    def __str__(self):
        return f"{self.asignatura_origen} - {self.estado_homologacion}"
