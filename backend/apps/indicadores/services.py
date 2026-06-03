from decimal import Decimal

from django.db import connection


def _round_decimal(value, places=2):
    if value is None:
        return None
    quantizer = Decimal("1").scaleb(-places)
    return Decimal(value).quantize(quantizer)


def _risk_label(score):
    if score <= 30:
        return "Bajo"
    if score <= 60:
        return "Medio"
    return "Alto"


def calculate_student_indicators(student):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            select count(distinct id_programa_asignatura)
            from reportes.vw_programa_asignatura_global
            where id_programa_academico = %s
              and estado = 'Activa'
            """,
            [student.id_programa_academico],
        )
        total_subjects = cursor.fetchone()[0] or 0

        cursor.execute(
            """
            select
                cod_asignatura,
                max(nota_final) as grade,
                max(coalesce(creditos, 0)) as credits
            from reportes.vw_inscripciones_detalle
            where id_estudiante = %s
              and estado_inscripcion = 'Aprobada'
              and nota_final is not null
            group by cod_asignatura
            """,
            [student.id_estudiante],
        )
        approved_rows = cursor.fetchall()

        cursor.execute(
            """
            select
                pa.cod_asignatura,
                max(h.nota_obtenida) as grade,
                max(coalesce(a.creditos, 0)) as credits
            from reportes.vw_homologaciones_global h
            join reportes.vw_programa_asignatura_global pa
              on pa.id_programa_asignatura = h.id_programa_asignatura
            left join institucional.asignatura a
              on a.cod_asignatura = pa.cod_asignatura
            where h.id_estudiante = %s
              and h.estado_homologacion = 'Aprobada'
              and h.nota_obtenida is not null
            group by pa.cod_asignatura
            """,
            [student.id_estudiante],
        )
        homologation_rows = cursor.fetchall()

        cursor.execute(
            """
            select
                count(distinct id_grupo) filter (
                    where estado_inscripcion = 'Reprobada'
                ) as failed_subjects,
                coalesce(bool_or(intento >= 3), false) as has_high_attempt
            from reportes.vw_inscripciones_detalle
            where id_estudiante = %s
            """,
            [student.id_estudiante],
        )
        failed_subjects, has_high_attempt = cursor.fetchone()

    approved_subjects = {}
    for subject_code, grade, credits in [*approved_rows, *homologation_rows]:
        current_grade = approved_subjects.get(subject_code, {}).get("grade")
        if current_grade is None or grade > current_grade:
            approved_subjects[subject_code] = {
                "grade": grade,
                "credits": credits,
            }

    approved_count = len(approved_subjects)
    missing_subjects = max(total_subjects - approved_count, 0)
    academic_progress = None
    if total_subjects:
        academic_progress = Decimal(approved_count) / Decimal(total_subjects) * 100

    weighted_points = sum(
        item["grade"] * item["credits"] for item in approved_subjects.values()
    )
    weighted_credits = sum(item["credits"] for item in approved_subjects.values())
    weighted_average = None
    performance_percentage = None
    if weighted_credits:
        weighted_average = weighted_points / Decimal(weighted_credits)
        performance_percentage = weighted_average / Decimal("5.0") * 100

    risk_score = 0
    if weighted_average is not None and weighted_average < Decimal("3.2"):
        risk_score += 30
    if failed_subjects >= 3:
        risk_score += 25
    if academic_progress is not None and academic_progress < Decimal("40"):
        risk_score += 20
    if student.estado_estudiante in {"Inactivo", "Suspendido", "Retirado"}:
        risk_score += 25
    if has_high_attempt:
        risk_score += 20
    risk_score = min(risk_score, 100)

    return {
        "student": student,
        "total_subjects": total_subjects,
        "approved_subjects": approved_count,
        "missing_subjects": missing_subjects,
        "academic_progress": _round_decimal(academic_progress),
        "weighted_average": _round_decimal(weighted_average),
        "performance_percentage": _round_decimal(performance_percentage),
        "failed_subjects": failed_subjects,
        "has_high_attempt": has_high_attempt,
        "risk_score": risk_score,
        "risk_label": _risk_label(risk_score),
        "has_enough_data": bool(total_subjects),
    }
