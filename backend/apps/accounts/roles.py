from django.db import DatabaseError
from django.urls import reverse

FUNCTIONAL_ROLES = (
    "estudiante",
    "docente",
    "coordinador",
    "decano",
    "administrativo",
    "superadmin",
)

ROLE_LABELS = {
    "estudiante": "Estudiante",
    "docente": "Docente",
    "coordinador": "Coordinador",
    "decano": "Decano",
    "administrativo": "Administrativo",
    "superadmin": "Superadmin",
}


def get_user_roles(user):
    if not user or not user.is_authenticated:
        return []

    roles = set()
    if user.is_superuser:
        roles.add("superadmin")

    try:
        group_roles = user.groups.filter(name__in=FUNCTIONAL_ROLES).values_list(
            "name",
            flat=True,
        )
        roles.update(group_roles)
    except DatabaseError:
        pass

    return sorted(roles, key=FUNCTIONAL_ROLES.index)


def user_has_role(user, role):
    return role in get_user_roles(user)


def get_role_labels(user):
    return [ROLE_LABELS[role] for role in get_user_roles(user)]


def get_dashboard_options(user):
    roles = get_user_roles(user)
    options = []

    role_options = {
        "estudiante": [
            {
                "title": "Mis inscripciones",
                "description": "Consultar mis materias, estados y notas registradas.",
                "url": reverse("academica:inscripcion_list"),
            },
            {
                "title": "Mi plan de estudios",
                "description": "Revisar asignaturas de mi programa academico.",
                "url": reverse("academica:plan_estudios_list"),
            },
            {
                "title": "Mis recibos",
                "description": "Consultar mis recibos y pagos de matricula.",
                "url": reverse("financiera:recibo_list"),
            },
            {
                "title": "Mis homologaciones",
                "description": "Consultar mis solicitudes de homologacion.",
                "url": reverse("homologaciones:homologacion_list"),
            },
            {
                "title": "Mis indicadores",
                "description": "Revisar avance, promedio y riesgo academico.",
                "url": reverse("indicadores:mi_indicador"),
            },
        ],
        "docente": [
            {
                "title": "Grupos asignados",
                "description": "Consultar grupos academicos y estudiantes inscritos.",
                "url": reverse("academica:grupo_list"),
            },
            {
                "title": "Perfil docente",
                "description": "Consultar docentes, asignaturas y cargos academicos.",
                "url": reverse("academica:profesor_list"),
            },
            {
                "title": "Indicadores de estudiantes",
                "description": "Consultar indicadores de estudiantes en mis grupos.",
                "url": reverse("indicadores:indicador_list"),
            },
        ],
        "coordinador": [
            {
                "title": "Agregar estudiante",
                "description": (
                    "Registrar un nuevo estudiante en el programa que coordinas."
                ),
                "url": reverse("academica:estudiante_create"),
            },
            {
                "title": "Gestion del programa",
                "description": "Consultar programas, planes de estudio y grupos.",
                "url": reverse("estructura:programa_list"),
            },
            {
                "title": "Oferta academica",
                "description": "Consultar grupos, asignaturas y prerrequisitos.",
                "url": reverse("academica:grupo_list"),
            },
            {
                "title": "Indicadores del programa",
                "description": "Consultar avance y riesgo de estudiantes del programa.",
                "url": reverse("indicadores:indicador_list"),
            },
        ],
        "decano": [
            {
                "title": "Gestion de facultad",
                "description": "Consultar facultades, programas y docentes.",
                "url": reverse("estructura:facultad_list"),
            },
            {
                "title": "Docentes",
                "description": "Consultar docentes, grupos y cargos academicos.",
                "url": reverse("academica:profesor_list"),
            },
            {
                "title": "Indicadores de facultad",
                "description": (
                    "Consultar avance y riesgo de estudiantes de la facultad."
                ),
                "url": reverse("indicadores:indicador_list"),
            },
        ],
        "administrativo": [
            {
                "title": "Procesos financieros",
                "description": (
                    "Consultar tarifas, recibos y matriculas de su facultad."
                ),
                "url": reverse("financiera:recibo_list"),
            },
        ],
        "superadmin": [
            {
                "title": "Agregar estudiante",
                "description": "Registrar estudiantes en cualquier programa activo.",
                "url": reverse("academica:estudiante_create"),
            },
            {
                "title": "Administracion general",
                "description": "Acceso general a los modulos de consulta.",
                "url": reverse("accounts:dashboard"),
            },
            {
                "title": "Auditoria",
                "description": "Consultar registros de auditoria del sistema.",
                "url": reverse("auditoria:auditoria_list"),
            },
        ],
    }

    seen = set()
    for role in roles:
        for option in role_options[role]:
            key = (option["title"], option["url"])
            if key not in seen:
                options.append({**option, "role": ROLE_LABELS[role]})
                seen.add(key)

    return options
