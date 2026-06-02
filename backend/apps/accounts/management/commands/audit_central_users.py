from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db.models import Count


class Command(BaseCommand):
    help = "Audita usuarios centrales sin imprimir contrasenas ni hashes."

    def handle(self, *args, **options):
        user_model = get_user_model()
        users = user_model.objects.prefetch_related("groups").order_by("correo")

        total = users.count()
        active = users.filter(is_active=True).count()
        inactive = users.filter(is_active=False).count()
        staff = users.filter(is_staff=True).count()
        superusers = users.filter(is_superuser=True).count()
        without_usable_password = sum(
            1 for user in users if not user.has_usable_password()
        )
        without_group = sum(1 for user in users if not user.groups.exists())
        empty_email = users.filter(correo__exact="").count()
        duplicate_emails = list(
            users.values("correo")
            .annotate(total=Count("id_usuario"))
            .filter(total__gt=1)
            .values_list("correo", flat=True)
        )
        group_names = list(
            Group.objects.order_by("name").values_list("name", flat=True)
        )

        self.stdout.write(f"Usuarios totales: {total}")
        self.stdout.write(f"Usuarios activos: {active}")
        self.stdout.write(f"Usuarios inactivos: {inactive}")
        self.stdout.write(f"Usuarios sin password usable: {without_usable_password}")
        self.stdout.write(f"Usuarios sin grupo: {without_group}")
        self.stdout.write(f"Usuarios staff: {staff}")
        self.stdout.write(f"Usuarios superuser: {superusers}")
        self.stdout.write(f"Correos vacios: {empty_email}")
        self.stdout.write(f"Correos duplicados: {len(duplicate_emails)}")
        self.stdout.write("Grupos existentes: " + ", ".join(group_names))

        self.stdout.write("Detalle seguro de usuarios:")
        for user in users:
            groups = ", ".join(user.groups.values_list("name", flat=True)) or "-"
            status = "activo" if user.is_active else "inactivo"
            self.stdout.write(
                f"- {user.correo or '(sin correo)'} | {status} | "
                f"staff={user.is_staff} | superuser={user.is_superuser} | "
                f"grupos={groups}"
            )
