from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import connection

DEMO_EMAIL = "admin.fing@universidad.edu"
DEMO_PASSWORD = "Demo12345*"


class Command(BaseCommand):
    help = "Crea la tabla public.usuario si falta y prepara el usuario demo central."

    def handle(self, *args, **options):
        user_model = get_user_model()
        existing_tables = set(connection.introspection.table_names())

        if user_model._meta.db_table not in existing_tables:
            with connection.schema_editor() as schema_editor:
                schema_editor.create_model(user_model)
            self.stdout.write("Tabla public.usuario creada con sus relaciones M2M.")
        else:
            self.stdout.write("Tabla public.usuario ya existe.")

        group, _ = Group.objects.get_or_create(name="superadmin")
        user, created = user_model.objects.update_or_create(
            correo=DEMO_EMAIL,
            defaults={
                "nombre": "Administrador Ingenieria",
                "tipo_de_documento": "CC",
                "numero_de_documento": "900000001",
                "direccion": "",
                "is_active": True,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        user.set_password(DEMO_PASSWORD)
        user.save(update_fields=["password"])
        user.groups.add(group)

        action = "creado" if created else "actualizado"
        self.stdout.write(self.style.SUCCESS(f"Usuario demo {DEMO_EMAIL} {action}."))
