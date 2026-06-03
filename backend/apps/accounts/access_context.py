from dataclasses import dataclass
from uuid import UUID

from django.db import connection
from django.db.models import Q

from apps.accounts.roles import get_user_roles


@dataclass(frozen=True)
class AccessContext:
    roles: frozenset[str]
    is_superadmin: bool
    id_usuario: UUID | None
    id_estudiante: UUID | None
    id_profesor: UUID | None
    id_administrativo: UUID | None
    id_facultad: str | None
    id_programa_academico: str | None
    student_ids: frozenset[UUID]
    professor_ids: frozenset[UUID]
    group_ids: frozenset[UUID]
    faculty_ids: frozenset[str]
    program_ids: frozenset[str]
    coordinated_program_ids: frozenset[str]
    dean_faculty_ids: frozenset[str]
    administrative_faculty_ids: frozenset[str]


def get_access_context(user):
    if not user or not user.is_authenticated:
        return _empty_context()

    cached = getattr(user, "_access_context", None)
    if cached is not None:
        return cached

    roles = frozenset(get_user_roles(user))
    id_usuario = user.id_usuario
    student_rows = _fetch_dicts(
        """
        select id_estudiante, id_facultad, id_programa_academico
        from reportes.vw_estudiantes_detalle
        where id_usuario = %s
        """,
        [id_usuario],
    )
    professor_rows = _fetch_dicts(
        """
        select id_profesor, id_facultad
        from reportes.vw_profesores_detalle
        where id_usuario = %s
        """,
        [id_usuario],
    )
    admin_rows = _fetch_dicts(
        """
        select id_administrativo, id_facultad
        from reportes.vw_administrativos_global
        where id_usuario = %s
        """,
        [id_usuario],
    )

    own_student_ids = {row["id_estudiante"] for row in student_rows}
    student_ids = set(own_student_ids)
    professor_ids = {row["id_profesor"] for row in professor_rows}
    faculty_ids = {row["id_facultad"] for row in student_rows + professor_rows}
    program_ids = {row["id_programa_academico"] for row in student_rows}

    coordinated_program_ids = _coordinated_program_ids(professor_ids)
    dean_faculty_ids = _dean_faculty_ids(professor_ids)
    administrative_faculty_ids = {row["id_facultad"] for row in admin_rows}

    faculty_ids.update(dean_faculty_ids)
    faculty_ids.update(administrative_faculty_ids)
    faculty_ids.update(_program_faculty_ids(coordinated_program_ids))
    program_ids.update(coordinated_program_ids)
    program_ids.update(_program_ids_for_faculties(dean_faculty_ids))
    program_ids.update(_program_ids_for_faculties(administrative_faculty_ids))

    if {"coordinador", "decano"} & roles:
        student_ids.update(_student_ids_for_programs(program_ids))
    if "administrativo" in roles:
        student_ids.update(_student_ids_for_faculties(administrative_faculty_ids))

    group_ids = set()
    if professor_ids:
        group_ids.update(_group_ids_for_professors(professor_ids))
    if own_student_ids:
        group_ids.update(_group_ids_for_students(own_student_ids))
    if {"coordinador", "decano", "administrativo"} & roles and program_ids:
        group_ids.update(_group_ids_for_programs(program_ids))

    context = AccessContext(
        roles=roles,
        is_superadmin="superadmin" in roles,
        id_usuario=id_usuario,
        id_estudiante=next(iter(student_ids), None),
        id_profesor=next(iter(professor_ids), None),
        id_administrativo=admin_rows[0]["id_administrativo"] if admin_rows else None,
        id_facultad=next(iter(faculty_ids), None),
        id_programa_academico=next(iter(program_ids), None),
        student_ids=frozenset(student_ids),
        professor_ids=frozenset(professor_ids),
        group_ids=frozenset(group_ids),
        faculty_ids=frozenset(faculty_ids),
        program_ids=frozenset(program_ids),
        coordinated_program_ids=frozenset(coordinated_program_ids),
        dean_faculty_ids=frozenset(dean_faculty_ids),
        administrative_faculty_ids=frozenset(administrative_faculty_ids),
    )
    user._access_context = context
    return context


def filter_estudiantes_for_user(queryset, user):
    context = get_access_context(user)
    if context.is_superadmin:
        return queryset
    query = Q()
    if "estudiante" in context.roles and context.student_ids:
        query |= Q(id_estudiante__in=context.student_ids)
    if {"coordinador", "decano", "administrativo"} & context.roles:
        if context.program_ids:
            query |= Q(id_programa_academico__in=context.program_ids)
        if context.faculty_ids:
            query |= Q(id_facultad__in=context.faculty_ids)
    return queryset.filter(query) if query else queryset.none()


def filter_profesores_for_user(queryset, user):
    context = get_access_context(user)
    if context.is_superadmin:
        return queryset
    query = Q()
    if "docente" in context.roles and context.professor_ids:
        query |= Q(id_profesor__in=context.professor_ids)
    if "coordinador" in context.roles and context.program_ids:
        query |= Q(id_profesor__in=_professor_ids_for_programs(context.program_ids))
    if {"decano", "administrativo"} & context.roles and context.faculty_ids:
        query |= Q(id_facultad__in=context.faculty_ids)
    return queryset.filter(query) if query else queryset.none()


def filter_grupos_for_user(queryset, user):
    context = get_access_context(user)
    if context.is_superadmin:
        return queryset
    query = Q()
    if {"estudiante", "docente"} & context.roles and context.group_ids:
        query |= Q(id_grupo__in=context.group_ids)
    if {"coordinador", "decano", "administrativo"} & context.roles:
        if context.program_ids:
            query |= Q(id_programa_academico__in=context.program_ids)
        if context.faculty_ids:
            query |= Q(id_facultad__in=context.faculty_ids)
    return queryset.filter(query) if query else queryset.none()


def filter_inscripciones_for_user(queryset, user):
    context = get_access_context(user)
    if context.is_superadmin:
        return queryset
    query = Q()
    if "estudiante" in context.roles and context.student_ids:
        query |= Q(id_estudiante__in=context.student_ids)
    if "docente" in context.roles and context.professor_ids:
        query |= Q(id_profesor__in=context.professor_ids)
    if {"coordinador", "decano", "administrativo"} & context.roles:
        if context.program_ids:
            query |= Q(id_programa_academico__in=context.program_ids)
        if context.faculty_ids:
            query |= Q(id_facultad__in=context.faculty_ids)
    return queryset.filter(query) if query else queryset.none()


def filter_homologaciones_for_user(queryset, user):
    context = get_access_context(user)
    if context.is_superadmin:
        return queryset
    query = Q()
    if "estudiante" in context.roles and context.student_ids:
        query |= Q(id_estudiante__in=context.student_ids)
    if "docente" in context.roles and context.professor_ids:
        query |= Q(id_profesor_evaluador__in=context.professor_ids)
    if "coordinador" in context.roles and context.program_ids:
        query |= Q(id_estudiante__in=_student_ids_for_programs(context.program_ids))
    if {"decano", "administrativo"} & context.roles and context.faculty_ids:
        query |= Q(id_facultad__in=context.faculty_ids)
    return queryset.filter(query) if query else queryset.none()


def filter_matriculas_for_user(queryset, user):
    context = get_access_context(user)
    if context.is_superadmin:
        return queryset
    query = Q()
    if "estudiante" in context.roles and context.student_ids:
        query |= Q(id_estudiante__in=context.student_ids)
    if {"coordinador", "decano", "administrativo"} & context.roles:
        if context.program_ids:
            query |= Q(id_programa_academico__in=context.program_ids)
        if context.faculty_ids:
            query |= Q(id_facultad__in=context.faculty_ids)
    return queryset.filter(query) if query else queryset.none()


def filter_recibos_for_user(queryset, user):
    context = get_access_context(user)
    if context.is_superadmin:
        return queryset
    query = Q()
    if "estudiante" in context.roles and context.student_ids:
        query |= Q(id_estudiante__in=context.student_ids)
    if "coordinador" in context.roles and context.program_ids:
        query |= Q(id_estudiante__in=_student_ids_for_programs(context.program_ids))
    if {"decano", "administrativo"} & context.roles and context.faculty_ids:
        query |= Q(id_facultad__in=context.faculty_ids)
    return queryset.filter(query) if query else queryset.none()


def filter_tarifas_for_user(queryset, user):
    context = get_access_context(user)
    if context.is_superadmin:
        return queryset
    query = Q()
    if {"coordinador", "decano", "administrativo"} & context.roles:
        if context.program_ids:
            query |= Q(programa_academico_id__in=context.program_ids)
        if context.faculty_ids:
            query |= Q(id_facultad__in=context.faculty_ids)
    return queryset.filter(query) if query else queryset.none()


def _empty_context():
    return AccessContext(
        roles=frozenset(),
        is_superadmin=False,
        id_usuario=None,
        id_estudiante=None,
        id_profesor=None,
        id_administrativo=None,
        id_facultad=None,
        id_programa_academico=None,
        student_ids=frozenset(),
        professor_ids=frozenset(),
        group_ids=frozenset(),
        faculty_ids=frozenset(),
        program_ids=frozenset(),
        coordinated_program_ids=frozenset(),
        dean_faculty_ids=frozenset(),
        administrative_faculty_ids=frozenset(),
    )


def _fetch_dicts(sql, params=None):
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]


def _fetch_values(sql, params=None):
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        return [row[0] for row in cursor.fetchall()]


def _coordinated_program_ids(professor_ids):
    if not professor_ids:
        return set()
    return set(
        _fetch_values(
            """
            select distinct id_programa_academico
            from reportes.vw_coordinadores_global
            where id_profesor = any(%s)
            """,
            [list(professor_ids)],
        ),
    )


def _dean_faculty_ids(professor_ids):
    if not professor_ids:
        return set()
    return set(
        _fetch_values(
            """
            select distinct id_facultad
            from reportes.vw_decanos_global
            where id_profesor = any(%s)
            """,
            [list(professor_ids)],
        ),
    )


def _program_faculty_ids(program_ids):
    if not program_ids:
        return set()
    return set(
        _fetch_values(
            """
            select distinct id_facultad
            from institucional.programa_academico
            where id_programa_academico = any(%s)
            """,
            [list(program_ids)],
        ),
    )


def _program_ids_for_faculties(faculty_ids):
    if not faculty_ids:
        return set()
    return set(
        _fetch_values(
            """
            select distinct id_programa_academico
            from institucional.programa_academico
            where id_facultad = any(%s)
            """,
            [list(faculty_ids)],
        ),
    )


def _group_ids_for_professors(professor_ids):
    return set(
        _fetch_values(
            """
            select distinct id_grupo
            from reportes.vw_grupos_detalle
            where id_profesor = any(%s)
            """,
            [list(professor_ids)],
        ),
    )


def _group_ids_for_students(student_ids):
    return set(
        _fetch_values(
            """
            select distinct id_grupo
            from reportes.vw_inscripciones_detalle
            where id_estudiante = any(%s)
            """,
            [list(student_ids)],
        ),
    )


def _group_ids_for_programs(program_ids):
    return set(
        _fetch_values(
            """
            select distinct id_grupo
            from reportes.vw_grupos_detalle
            where id_programa_academico = any(%s)
            """,
            [list(program_ids)],
        ),
    )


def _student_ids_for_programs(program_ids):
    if not program_ids:
        return set()
    return set(
        _fetch_values(
            """
            select distinct id_estudiante
            from reportes.vw_estudiantes_detalle
            where id_programa_academico = any(%s)
            """,
            [list(program_ids)],
        ),
    )


def _student_ids_for_faculties(faculty_ids):
    if not faculty_ids:
        return set()
    return set(
        _fetch_values(
            """
            select distinct id_estudiante
            from reportes.vw_estudiantes_detalle
            where id_facultad = any(%s)
            """,
            [list(faculty_ids)],
        ),
    )


def _professor_ids_for_programs(program_ids):
    if not program_ids:
        return set()
    return set(
        _fetch_values(
            """
            select distinct id_profesor
            from reportes.vw_grupos_detalle
            where id_programa_academico = any(%s)
              and id_profesor is not null
            """,
            [list(program_ids)],
        ),
    )
