from decimal import Decimal

from apps.academica.models import Inscripcion, ProgramaAsignatura
from apps.homologaciones.models import Homologacion


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
    total_subjects = ProgramaAsignatura.objects.filter(
        programa_academico=student.programa_academico,
        estado="Activa",
    ).count()

    approved_subjects = {}
    approved_enrollments = Inscripcion.objects.select_related(
        "grupo__programa_asignatura__asignatura",
    ).filter(
        estudiante=student,
        estado_inscripcion="Aprobada",
        nota_final__isnull=False,
    )
    for enrollment in approved_enrollments:
        subject = enrollment.grupo.programa_asignatura.asignatura
        current_grade = approved_subjects.get(subject.cod_asignatura, {}).get("grade")
        if current_grade is None or enrollment.nota_final > current_grade:
            approved_subjects[subject.cod_asignatura] = {
                "grade": enrollment.nota_final,
                "credits": subject.creditos,
                "source": "inscripcion",
            }

    approved_homologations = Homologacion.objects.select_related(
        "programa_asignatura__asignatura",
    ).filter(
        estudiante=student,
        estado_homologacion="Aprobada",
        nota_obtenida__isnull=False,
    )
    for homologation in approved_homologations:
        subject = homologation.programa_asignatura.asignatura
        current_grade = approved_subjects.get(subject.cod_asignatura, {}).get("grade")
        if current_grade is None or homologation.nota_obtenida > current_grade:
            approved_subjects[subject.cod_asignatura] = {
                "grade": homologation.nota_obtenida,
                "credits": subject.creditos,
                "source": "homologacion",
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

    failed_subjects = (
        Inscripcion.objects.filter(
            estudiante=student,
            estado_inscripcion="Reprobada",
        )
        .values("grupo__programa_asignatura__asignatura_id")
        .distinct()
        .count()
    )
    has_high_attempt = Inscripcion.objects.filter(
        estudiante=student,
        intento__gte=3,
    ).exists()

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
