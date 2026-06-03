from django.db import connection

from apps.estructura.models import Facultad, PeriodoAcademico, ProgramaAcademico
from apps.reportes.models import EstudianteDetalle, ProfesorDetalle


def _blank(label):
    return [("", label)]


def facultad_choices(blank_label="Todas las facultades"):
    rows = Facultad.objects.order_by("nombre_facultad").values_list(
        "id_facultad",
        "nombre_facultad",
    )
    return _blank(blank_label) + [(value, label) for value, label in rows]


def facultad_labels(ids):
    ids = [value for value in ids if value]
    if not ids:
        return {}
    rows = Facultad.objects.filter(id_facultad__in=ids).values_list(
        "id_facultad",
        "nombre_facultad",
    )
    return {value: label for value, label in rows}


def programa_choices(id_facultad=None, blank_label="Todos los programas"):
    queryset = ProgramaAcademico.objects.order_by("nombre_programa")
    if id_facultad:
        queryset = queryset.filter(facultad_id=id_facultad)
    rows = queryset.values_list("id_programa_academico", "nombre_programa")
    return _blank(blank_label) + [(value, label) for value, label in rows]


def programa_asignatura_labels(ids):
    ids = [value for value in ids if value]
    if not ids:
        return {}
    with connection.cursor() as cursor:
        cursor.execute(
            """
            select
                pa.id_programa_asignatura,
                coalesce(f.nombre_facultad, pa.id_facultad),
                coalesce(p.nombre_programa, pa.id_programa_academico),
                coalesce(a.nombre_asignatura, pa.cod_asignatura)
            from reportes.vw_programa_asignatura_global pa
            left join institucional.facultad f
              on f.id_facultad = pa.id_facultad
            left join institucional.programa_academico p
              on p.id_programa_academico = pa.id_programa_academico
            left join institucional.asignatura a
              on a.cod_asignatura = pa.cod_asignatura
            where pa.id_programa_asignatura = any(%s)
            """,
            [ids],
        )
        rows = cursor.fetchall()
    return {
        row[0]: f"{row[1]} - {row[2]} - {row[3]}"
        for row in rows
    }


def periodo_choices(blank_label="Todos los periodos"):
    rows = PeriodoAcademico.objects.order_by(
        "-fecha_inicio",
        "id_periodo_academico",
    ).values_list("id_periodo_academico", "id_periodo_academico")
    return _blank(blank_label) + [(value, label) for value, label in rows]


def distinct_choices(model, field, blank_label):
    values = (
        model.objects.exclude(**{f"{field}__isnull": True})
        .exclude(**{field: ""})
        .order_by(field)
        .values_list(field, flat=True)
        .distinct()
    )
    return _blank(blank_label) + [(value, value) for value in values]


def estudiante_labels(ids):
    ids = [value for value in ids if value]
    if not ids:
        return {}
    rows = EstudianteDetalle.objects.filter(id_estudiante__in=ids).values_list(
        "id_estudiante",
        "estudiante",
        "correo",
        "nombre_programa",
    )
    labels = {}
    for id_estudiante, estudiante, correo, programa in rows:
        principal = estudiante or correo or str(id_estudiante)
        secundario = correo or programa
        labels[id_estudiante] = (
            f"{principal} - {secundario}" if secundario else principal
        )
    return labels


def profesor_labels(ids):
    ids = [value for value in ids if value]
    if not ids:
        return {}
    rows = ProfesorDetalle.objects.filter(id_profesor__in=ids).values_list(
        "id_profesor",
        "profesor",
        "correo",
        "nombre_facultad",
    )
    labels = {}
    for id_profesor, profesor, correo, facultad in rows:
        principal = profesor or correo or str(id_profesor)
        secundario = correo or facultad
        labels[id_profesor] = f"{principal} - {secundario}" if secundario else principal
    return labels


def recibo_labels(ids):
    ids = [value for value in ids if value]
    if not ids:
        return {}
    with connection.cursor() as cursor:
        cursor.execute(
            """
            select
                r.id_recibo,
                coalesce(e.estudiante, e.correo, r.id_estudiante::text),
                coalesce(e.nombre_programa, tm.id_programa_academico),
                tm.id_periodo_academico
            from financiero.recibo r
            join financiero.tarifa_matricula tm
              on tm.id_tarifa_matricula = r.id_tarifa_matricula
            left join reportes.vw_estudiantes_detalle e
              on e.id_estudiante = r.id_estudiante
            where r.id_recibo = any(%s)
            """,
            [ids],
        )
        rows = cursor.fetchall()
    return {
        row[0]: f"{row[1]} - {row[2]} - {row[3]}"
        for row in rows
    }
