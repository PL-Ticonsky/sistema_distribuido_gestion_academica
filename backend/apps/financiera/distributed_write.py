import uuid

from django.core.exceptions import ValidationError
from django.db import connection

from apps.academica.distributed_write import (
    get_facultad_for_estudiante,
    get_fdw_schema_for_facultad,
)


def _matricula_table(id_facultad):
    schema = get_fdw_schema_for_facultad(id_facultad)
    return f'"{schema}"."matricula"'


def get_program_facultad(id_programa_academico):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            select id_facultad
            from institucional.programa_academico
            where id_programa_academico = %s
            """,
            [id_programa_academico],
        )
        row = cursor.fetchone()
    if row is None:
        raise ValidationError("No se encontro el programa academico seleccionado.")
    return row[0]


def get_recibo_context(id_recibo):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            select id_facultad, id_estudiante
            from financiero.recibo
            where id_recibo = %s
            """,
            [id_recibo],
        )
        row = cursor.fetchone()
    if row is None:
        raise ValidationError("No se encontro el recibo seleccionado.")
    get_fdw_schema_for_facultad(row[0])
    return {"id_facultad": row[0], "id_estudiante": row[1]}


def create_tarifa(
    *,
    id_programa_academico,
    id_periodo_academico,
    valor_matricula,
    fecha_limite_ordinaria,
    fecha_limite_extraordinaria,
    estado,
):
    id_tarifa_matricula = uuid.uuid4()
    id_facultad = get_program_facultad(id_programa_academico)
    with connection.cursor() as cursor:
        cursor.execute(
            """
            insert into financiero.tarifa_matricula (
                id_tarifa_matricula,
                id_programa_academico,
                id_facultad,
                id_periodo_academico,
                valor_matricula,
                fecha_limite_ordinaria,
                fecha_limite_extraordinaria,
                estado
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                id_tarifa_matricula,
                id_programa_academico,
                id_facultad,
                id_periodo_academico,
                valor_matricula,
                fecha_limite_ordinaria,
                fecha_limite_extraordinaria,
                estado,
            ],
        )
    return id_tarifa_matricula


def update_tarifa(
    *,
    id_tarifa_matricula,
    id_programa_academico,
    id_periodo_academico,
    valor_matricula,
    fecha_limite_ordinaria,
    fecha_limite_extraordinaria,
    estado,
):
    id_facultad = get_program_facultad(id_programa_academico)
    with connection.cursor() as cursor:
        cursor.execute(
            """
            update financiero.tarifa_matricula
            set id_programa_academico = %s,
                id_facultad = %s,
                id_periodo_academico = %s,
                valor_matricula = %s,
                fecha_limite_ordinaria = %s,
                fecha_limite_extraordinaria = %s,
                estado = %s
            where id_tarifa_matricula = %s
            """,
            [
                id_programa_academico,
                id_facultad,
                id_periodo_academico,
                valor_matricula,
                fecha_limite_ordinaria,
                fecha_limite_extraordinaria,
                estado,
                id_tarifa_matricula,
            ],
        )
        return cursor.rowcount


def deactivate_tarifa(*, id_tarifa_matricula):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            update financiero.tarifa_matricula
            set estado = %s
            where id_tarifa_matricula = %s
            """,
            ["Inactiva", id_tarifa_matricula],
        )
        return cursor.rowcount


def create_recibo(
    *,
    id_estudiante,
    id_tarifa_matricula,
    fecha_pago,
    valor_pagado,
    metodo_pago,
    estado_pago,
    extras,
):
    id_recibo = uuid.uuid4()
    id_facultad = get_facultad_for_estudiante(id_estudiante)
    with connection.cursor() as cursor:
        cursor.execute(
            """
            insert into financiero.recibo (
                id_recibo,
                id_estudiante,
                id_facultad,
                id_tarifa_matricula,
                fecha_pago,
                valor_pagado,
                metodo_pago,
                estado_pago,
                extras
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                id_recibo,
                id_estudiante,
                id_facultad,
                id_tarifa_matricula,
                fecha_pago,
                valor_pagado,
                metodo_pago,
                estado_pago,
                extras,
            ],
        )
    return id_recibo


def update_recibo(
    *,
    id_recibo,
    id_estudiante,
    id_tarifa_matricula,
    fecha_pago,
    valor_pagado,
    metodo_pago,
    estado_pago,
    extras,
):
    id_facultad = get_facultad_for_estudiante(id_estudiante)
    with connection.cursor() as cursor:
        cursor.execute(
            """
            update financiero.recibo
            set id_estudiante = %s,
                id_facultad = %s,
                id_tarifa_matricula = %s,
                fecha_pago = %s,
                valor_pagado = %s,
                metodo_pago = %s,
                estado_pago = %s,
                extras = %s
            where id_recibo = %s
            """,
            [
                id_estudiante,
                id_facultad,
                id_tarifa_matricula,
                fecha_pago,
                valor_pagado,
                metodo_pago,
                estado_pago,
                extras,
                id_recibo,
            ],
        )
        return cursor.rowcount


def anular_recibo(*, id_recibo):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            update financiero.recibo
            set estado_pago = %s
            where id_recibo = %s
            """,
            ["Anulado", id_recibo],
        )
        return cursor.rowcount


def create_matricula(*, id_recibo, estado_matricula):
    recibo = get_recibo_context(id_recibo)
    id_matricula = uuid.uuid4()
    table = _matricula_table(recibo["id_facultad"])
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            insert into {table} (
                id_matricula,
                id_facultad,
                id_estudiante,
                id_recibo,
                estado_matricula
            )
            values (%s, %s, %s, %s, %s)
            """,
            [
                id_matricula,
                recibo["id_facultad"],
                recibo["id_estudiante"],
                id_recibo,
                estado_matricula,
            ],
        )
    return id_matricula


def update_matricula(*, id_matricula, id_facultad, id_recibo, estado_matricula):
    recibo = get_recibo_context(id_recibo)
    table = _matricula_table(id_facultad)
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            update {table}
            set id_estudiante = %s,
                id_recibo = %s,
                estado_matricula = %s
            where id_matricula = %s
              and id_facultad = %s
            """,
            [
                recibo["id_estudiante"],
                id_recibo,
                estado_matricula,
                id_matricula,
                id_facultad,
            ],
        )
        return cursor.rowcount


def cancel_matricula(*, id_matricula, id_facultad):
    table = _matricula_table(id_facultad)
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            update {table}
            set estado_matricula = %s
            where id_matricula = %s
              and id_facultad = %s
            """,
            ["Cancelada", id_matricula, id_facultad],
        )
        return cursor.rowcount
