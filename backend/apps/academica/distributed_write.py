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
