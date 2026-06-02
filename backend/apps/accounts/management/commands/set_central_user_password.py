from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = (
        "Actualiza la contrasena de un usuario existente en "
        "seguridad.usuario_credencial."
    )

    def add_arguments(self, parser):
        parser.add_argument("correo")
        parser.add_argument("password")
        parser.add_argument(
            "--superuser",
            action="store_true",
            help=(
                "Marca el usuario como superusuario/staff en "
                "seguridad.usuario_credencial."
            ),
        )

    def handle(self, *args, **options):
        correo = options["correo"]
        encoded_password = make_password(options["password"])

        with connection.cursor() as cursor:
            cursor.execute(
                """
                select id_usuario
                from personas.usuario_dato_personal
                where lower(correo) = lower(%s)
                """,
                [correo],
            )
            row = cursor.fetchone()
            if row is None:
                raise CommandError(f"No existe un usuario central con correo {correo}.")

            if options["superuser"]:
                cursor.execute(
                    """
                    update seguridad.usuario_credencial
                    set password = %s,
                        is_superuser = true,
                        is_staff = true,
                        is_active = true
                    where id_usuario = %s
                    """,
                    [encoded_password, row[0]],
                )
            else:
                cursor.execute(
                    """
                    update seguridad.usuario_credencial
                    set password = %s
                    where id_usuario = %s
                    """,
                    [encoded_password, row[0]],
                )

        self.stdout.write(
            self.style.SUCCESS(f"Credencial central actualizada: {correo}"),
        )
