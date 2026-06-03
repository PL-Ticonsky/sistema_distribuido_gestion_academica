from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.accounts.roles import FUNCTIONAL_ROLES

ADMIN_EMAIL = "admin.fing@universidad.edu"


class Command(BaseCommand):
    help = "Normaliza passwords demo de usuarios centrales usando set_password()."

    def add_arguments(self, parser):
        parser.add_argument("--password", required=True)
        parser.add_argument("--all-users", action="store_true")
        mode = parser.add_mutually_exclusive_group(required=True)
        mode.add_argument("--dry-run", action="store_true")
        mode.add_argument("--apply", action="store_true")

    def handle(self, *args, **options):
        if not options["all_users"]:
            raise CommandError("Por ahora este comando requiere --all-users.")

        user_model = get_user_model()
        users = list(user_model.objects.prefetch_related("groups").order_by("correo"))
        password = options["password"]

        summary = {
            "total": len(users),
            "updated": 0,
            "verified_ok": 0,
            "verified_failed": 0,
            "omitted": 0,
            "groups_created": 0,
        }

        missing_groups = [
            role
            for role in FUNCTIONAL_ROLES
            if not Group.objects.filter(name=role).exists()
        ]

        if options["dry_run"]:
            summary["updated"] = len(users)
            self._print_summary("DRY-RUN", summary, len(missing_groups))
            return

        with transaction.atomic():
            for role in missing_groups:
                Group.objects.create(name=role)
                summary["groups_created"] += 1

            superadmin_group = Group.objects.get(name="superadmin")

            for user in users:
                user.set_password(password)
                user.is_active = True
                user.save(update_fields=["password", "is_active"])
                summary["updated"] += 1

                if user.check_password(password):
                    summary["verified_ok"] += 1
                else:
                    summary["verified_failed"] += 1

            try:
                admin_user = user_model.objects.get(correo=ADMIN_EMAIL)
            except user_model.DoesNotExist:
                summary["omitted"] += 1
            else:
                admin_user.is_active = True
                admin_user.is_staff = True
                admin_user.is_superuser = True
                admin_user.save(
                    update_fields=["is_active", "is_staff", "is_superuser"]
                )
                admin_user.groups.add(superadmin_group)

        self._print_summary("APPLY", summary, len(missing_groups))

    def _print_summary(self, prefix, summary, missing_groups):
        self.stdout.write(f"{prefix}: usuarios totales: {summary['total']}")
        self.stdout.write(f"{prefix}: usuarios actualizados: {summary['updated']}")
        self.stdout.write(f"{prefix}: verificados OK: {summary['verified_ok']}")
        self.stdout.write(
            f"{prefix}: verificados fallidos: {summary['verified_failed']}"
        )
        self.stdout.write(f"{prefix}: usuarios omitidos: {summary['omitted']}")
        self.stdout.write(f"{prefix}: grupos faltantes detectados: {missing_groups}")
        self.stdout.write(f"{prefix}: grupos creados: {summary['groups_created']}")
