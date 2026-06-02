from django.db import connection

from apps.accounts.roles import get_user_roles


def is_superadmin(user):
    return "superadmin" in get_user_roles(user)


def get_student_for_user(user):
    from apps.academica.models import Estudiante

    if not user or not user.is_authenticated:
        return None

    return (
        Estudiante.objects.select_related("usuario", "programa_academico")
        .filter(usuario=user)
        .first()
    )


def get_professor_for_user(user):
    from apps.academica.models import Profesor

    if not user or not user.is_authenticated:
        return None

    return (
        Profesor.objects.select_related("usuario", "facultad")
        .filter(usuario=user)
        .first()
    )


def get_coordinated_program_ids(user):
    from apps.academica.models import Coordinador

    professor = get_professor_for_user(user)
    if not professor:
        return []

    return list(
        Coordinador.objects.filter(profesor=professor).values_list(
            "programa_academico_id",
            flat=True,
        ),
    )


def get_dean_faculty_ids(user):
    from apps.academica.models import Decano

    professor = get_professor_for_user(user)
    if not professor:
        return []

    return list(
        Decano.objects.filter(profesor=professor).values_list(
            "facultad_id",
            flat=True,
        ),
    )


def get_administrative_faculty_ids(user):
    if not user or not user.is_authenticated:
        return []

    with connection.cursor() as cursor:
        cursor.execute(
            """
            select id_facultad
            from administrativo
            where id_usuario = %s
            """,
            [user.id_usuario],
        )
        return [row[0] for row in cursor.fetchall()]


def get_program_ids_for_faculties(faculty_ids):
    from apps.estructura.models import ProgramaAcademico

    if not faculty_ids:
        return []

    return list(
        ProgramaAcademico.objects.filter(facultad_id__in=faculty_ids).values_list(
            "id_programa_academico",
            flat=True,
        ),
    )


def get_visible_program_ids(user, *, include_student=False, include_teacher=False):
    from apps.academica.models import Grupo

    roles = set(get_user_roles(user))
    program_ids = set()

    if is_superadmin(user):
        return None

    if "coordinador" in roles:
        program_ids.update(get_coordinated_program_ids(user))

    if "decano" in roles:
        program_ids.update(get_program_ids_for_faculties(get_dean_faculty_ids(user)))

    if include_student and "estudiante" in roles:
        student = get_student_for_user(user)
        if student:
            program_ids.add(student.programa_academico_id)

    if include_teacher and "docente" in roles:
        professor = get_professor_for_user(user)
        if professor:
            program_ids.update(
                Grupo.objects.filter(profesor=professor).values_list(
                    "programa_asignatura__programa_academico_id",
                    flat=True,
                ),
            )

    return list(program_ids)


def get_visible_faculty_ids(user):
    roles = set(get_user_roles(user))
    faculty_ids = set()

    if is_superadmin(user):
        return None

    if "coordinador" in roles:
        faculty_ids.update(
            get_program_faculty_ids(get_coordinated_program_ids(user)),
        )

    if "decano" in roles:
        faculty_ids.update(get_dean_faculty_ids(user))

    return list(faculty_ids)


def get_program_faculty_ids(program_ids):
    from apps.estructura.models import ProgramaAcademico

    if not program_ids:
        return []

    return list(
        ProgramaAcademico.objects.filter(
            id_programa_academico__in=program_ids,
        ).values_list("facultad_id", flat=True),
    )


def get_visible_student_ids(user):
    from apps.academica.models import Estudiante

    roles = set(get_user_roles(user))
    student_ids = set()

    if is_superadmin(user):
        return None

    if "estudiante" in roles:
        student = get_student_for_user(user)
        if student:
            student_ids.add(student.id_estudiante)

    program_ids = get_visible_program_ids(user)
    if program_ids:
        student_ids.update(
            Estudiante.objects.filter(
                programa_academico_id__in=program_ids
            ).values_list(
                "id_estudiante",
                flat=True,
            ),
        )

    if "administrativo" in roles:
        admin_program_ids = get_program_ids_for_faculties(
            get_administrative_faculty_ids(user),
        )
        student_ids.update(
            Estudiante.objects.filter(
                programa_academico_id__in=admin_program_ids,
            ).values_list("id_estudiante", flat=True),
        )

    return list(student_ids)


def get_visible_group_ids(user):
    from apps.academica.models import Grupo, Inscripcion

    roles = set(get_user_roles(user))
    group_ids = set()

    if is_superadmin(user):
        return None

    if "docente" in roles:
        professor = get_professor_for_user(user)
        if professor:
            group_ids.update(
                Grupo.objects.filter(profesor=professor).values_list(
                    "id_grupo", flat=True
                ),
            )

    if "estudiante" in roles:
        student = get_student_for_user(user)
        if student:
            group_ids.update(
                Inscripcion.objects.filter(estudiante=student).values_list(
                    "grupo_id",
                    flat=True,
                ),
            )

    program_ids = get_visible_program_ids(user)
    if program_ids:
        group_ids.update(
            Grupo.objects.filter(
                programa_asignatura__programa_academico_id__in=program_ids,
            ).values_list("id_grupo", flat=True),
        )

    return list(group_ids)


def get_visible_professor_ids(user):
    from apps.academica.models import Grupo, Profesor

    roles = set(get_user_roles(user))
    professor_ids = set()

    if is_superadmin(user):
        return None

    if "docente" in roles:
        professor = get_professor_for_user(user)
        if professor:
            professor_ids.add(professor.id_profesor)

    if "decano" in roles:
        faculty_ids = get_dean_faculty_ids(user)
        professor_ids.update(
            Profesor.objects.filter(facultad_id__in=faculty_ids).values_list(
                "id_profesor",
                flat=True,
            ),
        )

    if "coordinador" in roles:
        program_ids = get_coordinated_program_ids(user)
        professor_ids.update(
            Grupo.objects.filter(
                programa_asignatura__programa_academico_id__in=program_ids,
                profesor__isnull=False,
            ).values_list("profesor_id", flat=True),
        )

    return list(professor_ids)
