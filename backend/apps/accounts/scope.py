from apps.accounts.access_context import get_access_context
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
    return list(get_access_context(user).coordinated_program_ids)


def get_dean_faculty_ids(user):
    return list(get_access_context(user).dean_faculty_ids)


def get_administrative_faculty_ids(user):
    return list(get_access_context(user).administrative_faculty_ids)


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
    context = get_access_context(user)
    if context.is_superadmin:
        return None
    return list(context.program_ids)


def get_visible_faculty_ids(user):
    context = get_access_context(user)
    if context.is_superadmin:
        return None
    return list(context.faculty_ids)


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
    context = get_access_context(user)
    if context.is_superadmin:
        return None
    return list(context.student_ids)


def get_visible_group_ids(user):
    context = get_access_context(user)
    if context.is_superadmin:
        return None
    return list(context.group_ids)


def get_visible_professor_ids(user):
    context = get_access_context(user)
    if context.is_superadmin:
        return None
    return list(context.professor_ids)
