from django.db import models


class UsuarioGlobal(models.Model):
    id_usuario = models.UUIDField(primary_key=True)
    nombre = models.CharField(max_length=80)
    tipo_de_documento = models.CharField(max_length=2)
    numero_de_documento = models.CharField(max_length=20)
    correo = models.EmailField(max_length=254)
    direccion = models.CharField(max_length=120, blank=True, null=True)  # noqa: DJ001
    last_login = models.DateTimeField(blank=True, null=True)  # noqa: DJ001
    is_superuser = models.BooleanField()
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = '"reportes"."vw_usuarios_global"'
        ordering = ["nombre"]


class EstudianteDetalle(models.Model):
    nodo_origen = models.TextField(blank=True, null=True)  # noqa: DJ001
    id_estudiante = models.UUIDField(primary_key=True)
    id_usuario = models.UUIDField(blank=True, null=True)  # noqa: DJ001
    id_facultad = models.CharField(max_length=10, blank=True, null=True)  # noqa: DJ001
    nombre_facultad = models.CharField(max_length=80, blank=True, null=True)  # noqa: DJ001
    id_programa_academico = models.CharField(max_length=20, blank=True, null=True)  # noqa: DJ001
    nombre_programa = models.CharField(max_length=100, blank=True, null=True)  # noqa: DJ001
    estudiante = models.CharField(max_length=160, blank=True, null=True)  # noqa: DJ001
    correo = models.EmailField(max_length=254, blank=True, null=True)  # noqa: DJ001
    estado_estudiante = models.CharField(max_length=20, blank=True, null=True)  # noqa: DJ001
    limite_matriculas = models.IntegerField(blank=True, null=True)  # noqa: DJ001

    class Meta:
        managed = False
        db_table = '"reportes"."vw_estudiantes_detalle"'
        ordering = ["nombre_facultad", "nombre_programa", "estudiante"]


class ProfesorDetalle(models.Model):
    nodo_origen = models.TextField(blank=True, null=True)  # noqa: DJ001
    id_profesor = models.UUIDField(primary_key=True)
    id_usuario = models.UUIDField(blank=True, null=True)  # noqa: DJ001
    id_facultad = models.CharField(max_length=10, blank=True, null=True)  # noqa: DJ001
    nombre_facultad = models.CharField(max_length=80, blank=True, null=True)  # noqa: DJ001
    profesor = models.CharField(max_length=160, blank=True, null=True)  # noqa: DJ001
    correo = models.EmailField(max_length=254, blank=True, null=True)  # noqa: DJ001
    categoria = models.CharField(max_length=40, blank=True, null=True)  # noqa: DJ001
    vinculacion = models.CharField(max_length=40, blank=True, null=True)  # noqa: DJ001

    class Meta:
        managed = False
        db_table = '"reportes"."vw_profesores_detalle"'
        ordering = ["nombre_facultad", "profesor"]


class GrupoDetalle(models.Model):
    nodo_origen = models.TextField(blank=True, null=True)  # noqa: DJ001
    id_grupo = models.UUIDField(primary_key=True)
    id_facultad = models.CharField(max_length=10, blank=True, null=True)  # noqa: DJ001
    nombre_facultad = models.CharField(max_length=80, blank=True, null=True)  # noqa: DJ001
    id_periodo_academico = models.CharField(max_length=10, blank=True, null=True)  # noqa: DJ001
    id_programa_academico = models.CharField(max_length=20, blank=True, null=True)  # noqa: DJ001
    nombre_programa = models.CharField(max_length=100, blank=True, null=True)  # noqa: DJ001
    id_programa_asignatura = models.UUIDField(blank=True, null=True)  # noqa: DJ001
    cod_asignatura = models.CharField(max_length=20, blank=True, null=True)  # noqa: DJ001
    nombre_asignatura = models.CharField(max_length=120, blank=True, null=True)  # noqa: DJ001
    creditos = models.IntegerField(blank=True, null=True)  # noqa: DJ001
    codigo_grupo = models.CharField(max_length=20, blank=True, null=True)  # noqa: DJ001
    estado_grupo = models.CharField(max_length=20, blank=True, null=True)  # noqa: DJ001
    cupo_maximo = models.IntegerField(blank=True, null=True)  # noqa: DJ001
    id_profesor = models.UUIDField(blank=True, null=True)  # noqa: DJ001
    profesor = models.CharField(max_length=160, blank=True, null=True)  # noqa: DJ001

    class Meta:
        managed = False
        db_table = '"reportes"."vw_grupos_detalle"'
        ordering = ["nombre_facultad", "id_periodo_academico", "codigo_grupo"]


class InscripcionDetalle(models.Model):
    nodo_origen = models.TextField(blank=True, null=True)  # noqa: DJ001
    id_inscripcion = models.UUIDField(primary_key=True)
    id_facultad = models.CharField(max_length=10, blank=True, null=True)  # noqa: DJ001
    nombre_facultad = models.CharField(max_length=80, blank=True, null=True)  # noqa: DJ001
    id_estudiante = models.UUIDField(blank=True, null=True)  # noqa: DJ001
    estudiante = models.CharField(max_length=160, blank=True, null=True)  # noqa: DJ001
    id_programa_academico = models.CharField(max_length=20, blank=True, null=True)  # noqa: DJ001
    nombre_programa = models.CharField(max_length=100, blank=True, null=True)  # noqa: DJ001
    id_periodo_academico = models.CharField(max_length=10, blank=True, null=True)  # noqa: DJ001
    cod_asignatura = models.CharField(max_length=20, blank=True, null=True)  # noqa: DJ001
    nombre_asignatura = models.CharField(max_length=120, blank=True, null=True)  # noqa: DJ001
    creditos = models.IntegerField(blank=True, null=True)  # noqa: DJ001
    id_grupo = models.UUIDField(blank=True, null=True)  # noqa: DJ001
    codigo_grupo = models.CharField(max_length=20, blank=True, null=True)  # noqa: DJ001
    id_profesor = models.UUIDField(blank=True, null=True)  # noqa: DJ001
    profesor = models.CharField(max_length=160, blank=True, null=True)  # noqa: DJ001
    nota_final = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
    )  # noqa: DJ001
    intento = models.IntegerField(blank=True, null=True)  # noqa: DJ001
    estado_inscripcion = models.CharField(max_length=20, blank=True, null=True)  # noqa: DJ001

    class Meta:
        managed = False
        db_table = '"reportes"."vw_inscripciones_detalle"'
        ordering = ["nombre_facultad", "estudiante", "nombre_asignatura"]


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
        db_table = '"reportes"."vw_matriculas_detalle"'
        ordering = ["nombre_facultad", "estudiante", "id_periodo_academico"]


class HomologacionGlobal(models.Model):
    nodo_origen = models.TextField(blank=True, null=True)  # noqa: DJ001
    id_homologacion = models.UUIDField(primary_key=True)
    id_facultad = models.CharField(max_length=10, blank=True, null=True)  # noqa: DJ001
    id_profesor_evaluador = models.UUIDField(blank=True, null=True)  # noqa: DJ001
    id_estudiante = models.UUIDField(blank=True, null=True)  # noqa: DJ001
    asignatura_origen = models.CharField(max_length=120, blank=True, null=True)  # noqa: DJ001
    institucion_origen = models.CharField(max_length=120, blank=True, null=True)  # noqa: DJ001
    id_programa_asignatura = models.UUIDField(blank=True, null=True)  # noqa: DJ001
    fecha_solicitud = models.DateField(blank=True, null=True)  # noqa: DJ001
    estado_homologacion = models.CharField(max_length=20, blank=True, null=True)  # noqa: DJ001
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
        db_table = '"reportes"."vw_homologaciones_global"'
        ordering = ["-fecha_solicitud", "id_homologacion"]
