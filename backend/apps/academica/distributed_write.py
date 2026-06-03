import uuid

from django.core.exceptions import ValidationError
from django.db import connection

FACULTAD_TO_FDW = {
    "FING": "fdw_ingenieria",
    "FCE": "fdw_ciencias_educacion",
    "FTEC": "fdw_tecnologica",
    "FMA": "fdw_medio_ambiente",
    "FART": "fdw_artes",
}


def get_fdw_schema_for_facultad(id_facultad):
    try:
        return FACULTAD_TO_FDW[id_facultad]
    except KeyError as exc:
        raise ValidationError(
            f"La facultad {id_facultad!r} no tiene esquema FDW configurado.",
        ) from exc


def _estudiante_table(id_facultad):
    schema = get_fdw_schema_for_facultad(id_facultad)
    return f'"{schema}"."estudiante"'


def _grupo_table(id_facultad):
    schema = get_fdw_schema_for_facultad(id_facultad)
    return f'"{schema}"."grupo"'


def _inscripcion_table(id_facultad):
    schema = get_fdw_schema_for_facultad(id_facultad)
    return f'"{schema}"."inscripcion"'


def _homologacion_table(id_facultad):
    schema = get_fdw_schema_for_facultad(id_facultad)
    return f'"{schema}"."homologacion"'


def get_facultad_for_grupo(id_grupo):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            select id_facultad
            from reportes.vw_grupos_detalle
            where id_grupo = %s
            """,
            [id_grupo],
        )
        row = cursor.fetchone()
    if row is None:
        raise ValidationError("No se encontro el grupo seleccionado.")
    get_fdw_schema_for_facultad(row[0])
    return row[0]


def get_facultad_for_estudiante(id_estudiante):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            select id_facultad
            from reportes.vw_estudiantes_detalle
            where id_estudiante = %s
            """,
            [id_estudiante],
        )
        row = cursor.fetchone()
    if row is None:
        raise ValidationError("No se encontro el estudiante seleccionado.")
    get_fdw_schema_for_facultad(row[0])
    return row[0]


def create_estudiante(
    *,
    id_usuario,
    id_facultad,
    id_programa_academico,
    limite_matriculas,
    estado_estudiante,
):
    id_estudiante = uuid.uuid4()
    table = _estudiante_table(id_facultad)
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            insert into {table} (
                id_estudiante,
                id_usuario,
                id_facultad,
                id_programa_academico,
                limite_matriculas,
                estado_estudiante
            )
            values (%s, %s, %s, %s, %s, %s)
            """,
            [
                id_estudiante,
                id_usuario,
                id_facultad,
                id_programa_academico,
                limite_matriculas,
                estado_estudiante,
            ],
        )
    return id_estudiante


def update_estudiante(
    *,
    id_estudiante,
    id_usuario,
    id_facultad,
    id_programa_academico,
    limite_matriculas,
    estado_estudiante,
):
    table = _estudiante_table(id_facultad)
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            update {table}
            set id_usuario = %s,
                id_programa_academico = %s,
                limite_matriculas = %s,
                estado_estudiante = %s
            where id_estudiante = %s
              and id_facultad = %s
            """,
            [
                id_usuario,
                id_programa_academico,
                limite_matriculas,
                estado_estudiante,
                id_estudiante,
                id_facultad,
            ],
        )
        return cursor.rowcount


def delete_or_deactivate_estudiante(*, id_estudiante, id_facultad):
    table = _estudiante_table(id_facultad)
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            update {table}
            set estado_estudiante = %s
            where id_estudiante = %s
              and id_facultad = %s
            """,
            ["Inactivo", id_estudiante, id_facultad],
        )
        return cursor.rowcount


def create_grupo(
    *,
    id_facultad,
    id_programa_asignatura,
    id_periodo_academico,
    id_profesor,
    codigo_grupo,
    cupo_maximo,
    estado_grupo,
):
    id_grupo = uuid.uuid4()
    table = _grupo_table(id_facultad)
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            insert into {table} (
                id_grupo,
                id_facultad,
                id_programa_asignatura,
                id_periodo_academico,
                id_profesor,
                codigo_grupo,
                cupo_maximo,
                estado_grupo
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                id_grupo,
                id_facultad,
                id_programa_asignatura,
                id_periodo_academico,
                id_profesor,
                codigo_grupo,
                cupo_maximo,
                estado_grupo,
            ],
        )
    return id_grupo


def update_grupo(
    *,
    id_grupo,
    id_facultad,
    id_programa_asignatura,
    id_periodo_academico,
    id_profesor,
    codigo_grupo,
    cupo_maximo,
    estado_grupo,
):
    table = _grupo_table(id_facultad)
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            update {table}
            set id_programa_asignatura = %s,
                id_periodo_academico = %s,
                id_profesor = %s,
                codigo_grupo = %s,
                cupo_maximo = %s,
                estado_grupo = %s
            where id_grupo = %s
              and id_facultad = %s
            """,
            [
                id_programa_asignatura,
                id_periodo_academico,
                id_profesor,
                codigo_grupo,
                cupo_maximo,
                estado_grupo,
                id_grupo,
                id_facultad,
            ],
        )
        return cursor.rowcount


def deactivate_or_cancel_grupo(*, id_grupo, id_facultad):
    table = _grupo_table(id_facultad)
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            update {table}
            set estado_grupo = %s
            where id_grupo = %s
              and id_facultad = %s
            """,
            ["Cancelado", id_grupo, id_facultad],
        )
        return cursor.rowcount


def create_inscripcion(
    *,
    id_estudiante,
    id_grupo,
    nota1,
    nota2,
    nota3,
    nota_final,
    intento,
    estado_inscripcion,
):
    id_inscripcion = uuid.uuid4()
    id_facultad = get_facultad_for_grupo(id_grupo)
    table = _inscripcion_table(id_facultad)
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            insert into {table} (
                id_inscripcion,
                id_facultad,
                id_grupo,
                id_estudiante,
                nota1,
                nota2,
                nota3,
                nota_final,
                intento,
                estado_inscripcion
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                id_inscripcion,
                id_facultad,
                id_grupo,
                id_estudiante,
                nota1,
                nota2,
                nota3,
                nota_final,
                intento,
                estado_inscripcion,
            ],
        )
    return id_inscripcion


def update_inscripcion(
    *,
    id_inscripcion,
    id_facultad,
    id_estudiante,
    id_grupo,
    nota1,
    nota2,
    nota3,
    nota_final,
    intento,
    estado_inscripcion,
):
    table = _inscripcion_table(id_facultad)
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            update {table}
            set id_estudiante = %s,
                id_grupo = %s,
                nota1 = %s,
                nota2 = %s,
                nota3 = %s,
                nota_final = %s,
                intento = %s,
                estado_inscripcion = %s
            where id_inscripcion = %s
              and id_facultad = %s
            """,
            [
                id_estudiante,
                id_grupo,
                nota1,
                nota2,
                nota3,
                nota_final,
                intento,
                estado_inscripcion,
                id_inscripcion,
                id_facultad,
            ],
        )
        return cursor.rowcount


def cancel_inscripcion(*, id_inscripcion, id_facultad):
    table = _inscripcion_table(id_facultad)
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            update {table}
            set estado_inscripcion = %s
            where id_inscripcion = %s
              and id_facultad = %s
            """,
            ["Cancelada", id_inscripcion, id_facultad],
        )
        return cursor.rowcount


def create_homologacion(
    *,
    id_profesor_evaluador,
    id_estudiante,
    asignatura_origen,
    institucion_origen,
    id_programa_asignatura,
    fecha_solicitud,
    estado_homologacion,
):
    id_homologacion = uuid.uuid4()
    id_facultad = get_facultad_for_estudiante(id_estudiante)
    table = _homologacion_table(id_facultad)
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            insert into {table} (
                id_homologacion,
                id_facultad,
                id_profesor_evaluador,
                id_estudiante,
                asignatura_origen,
                institucion_origen,
                id_programa_asignatura,
                fecha_solicitud,
                estado_homologacion
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                id_homologacion,
                id_facultad,
                id_profesor_evaluador,
                id_estudiante,
                asignatura_origen,
                institucion_origen,
                id_programa_asignatura,
                fecha_solicitud,
                estado_homologacion,
            ],
        )
    return id_homologacion


def update_homologacion(
    *,
    id_homologacion,
    id_facultad,
    id_profesor_evaluador,
    id_estudiante,
    asignatura_origen,
    institucion_origen,
    id_programa_asignatura,
    fecha_solicitud,
    estado_homologacion,
    observacion,
    fecha_respuesta,
    nota_obtenida,
):
    table = _homologacion_table(id_facultad)
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            update {table}
            set id_profesor_evaluador = %s,
                id_estudiante = %s,
                asignatura_origen = %s,
                institucion_origen = %s,
                id_programa_asignatura = %s,
                fecha_solicitud = %s,
                estado_homologacion = %s,
                observacion = %s,
                fecha_respuesta = %s,
                nota_obtenida = %s
            where id_homologacion = %s
              and id_facultad = %s
            """,
            [
                id_profesor_evaluador,
                id_estudiante,
                asignatura_origen,
                institucion_origen,
                id_programa_asignatura,
                fecha_solicitud,
                estado_homologacion,
                observacion,
                fecha_respuesta,
                nota_obtenida,
                id_homologacion,
                id_facultad,
            ],
        )
        return cursor.rowcount


def asignar_evaluador_homologacion(
    *,
    id_homologacion,
    id_facultad,
    id_profesor_evaluador,
):
    table = _homologacion_table(id_facultad)
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            update {table}
            set id_profesor_evaluador = %s,
                estado_homologacion = %s
            where id_homologacion = %s
              and id_facultad = %s
            """,
            [
                id_profesor_evaluador,
                "En revision",
                id_homologacion,
                id_facultad,
            ],
        )
        return cursor.rowcount


def evaluar_homologacion(
    *,
    id_homologacion,
    id_facultad,
    estado_homologacion,
    observacion,
    fecha_respuesta,
    nota_obtenida,
):
    table = _homologacion_table(id_facultad)
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            update {table}
            set estado_homologacion = %s,
                observacion = %s,
                fecha_respuesta = %s,
                nota_obtenida = %s
            where id_homologacion = %s
              and id_facultad = %s
            """,
            [
                estado_homologacion,
                observacion,
                fecha_respuesta,
                nota_obtenida,
                id_homologacion,
                id_facultad,
            ],
        )
        return cursor.rowcount


def cancel_homologacion(*, id_homologacion, id_facultad):
    table = _homologacion_table(id_facultad)
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            update {table}
            set estado_homologacion = %s
            where id_homologacion = %s
              and id_facultad = %s
            """,
            ["Cancelada", id_homologacion, id_facultad],
        )
        return cursor.rowcount
