from django.core.management.base import BaseCommand

from apps.accounts.models import CustomUser
from apps.accounts.roles import FUNCTIONAL_ROLES

try:
    from django.contrib.auth.models import Group
except ImportError:  # pragma: no cover
    Group = None

DEMO_PASSWORD = "Demo12345*"

ROLE_MAP = {
    "Administrador funcional": "superadmin",
    "Estudiante": "estudiante",
    "Profesor": "docente",
    "Coordinador": "coordinador",
    "Decano": "decano",
    "Administrativo": "administrativo",
}

DEMO_USERS = [
    {
        "rol": "Administrador funcional",
        "nombre": "Claudia Benitez",
        "correo": "claudia.benitez@universidad.edu",
        "tipo_de_documento": "CC",
        "numero_de_documento": "100000020",
        "direccion": "Carrera 6 13-29",
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "rol": "Estudiante",
        "nombre": "Sofia Herrera",
        "correo": "sofia.herrera@universidad.edu",
        "tipo_de_documento": "CC",
        "numero_de_documento": "100000009",
        "direccion": "Calle 45 20-11",
    },
    {
        "rol": "Profesor",
        "nombre": "Carolina Vargas",
        "correo": "carolina.vargas@universidad.edu",
        "tipo_de_documento": "CC",
        "numero_de_documento": "100000003",
        "direccion": "Calle 25 4-18",
        "is_staff": True,
    },
    {
        "rol": "Coordinador",
        "nombre": "Miguel Rojas",
        "correo": "miguel.rojas@universidad.edu",
        "tipo_de_documento": "CC",
        "numero_de_documento": "100000002",
        "direccion": "Carrera 8 22-14",
        "is_staff": True,
    },
    {
        "rol": "Decano",
        "nombre": "Laura Perez",
        "correo": "laura.perez@universidad.edu",
        "tipo_de_documento": "CC",
        "numero_de_documento": "100000001",
        "direccion": "Calle 10 15-20",
        "is_staff": True,
    },
    {
        "rol": "Administrativo",
        "nombre": "Hector Suarez",
        "correo": "hector.suarez@universidad.edu",
        "tipo_de_documento": "CC",
        "numero_de_documento": "100000021",
        "direccion": "Calle 9 24-31",
        "is_staff": True,
    },
]


class Command(BaseCommand):
    help = "Crea usuarios demo locales con contrasenas hasheadas por Django."

    def handle(self, *args, **options):
        groups = {}
        if Group is not None:
            for role in FUNCTIONAL_ROLES:
                group, _ = Group.objects.get_or_create(name=role)
                groups[role] = group

        for item in DEMO_USERS:
            data = {
                "is_staff": False,
                "is_superuser": False,
                "is_active": True,
                **item,
            }
            rol = data.pop("rol")
            correo = data["correo"]
            user, created = CustomUser.objects.update_or_create(
                correo=correo,
                defaults=data,
            )
            user.set_password(DEMO_PASSWORD)
            user.save()

            group_name = ROLE_MAP[rol]
            if group_name in groups:
                user.groups.add(groups[group_name])

            action = "creado" if created else "actualizado"
            self.stdout.write(f"{correo} ({rol}) {action}.")

        self.stdout.write(self.style.SUCCESS("Usuarios demo locales listos."))
