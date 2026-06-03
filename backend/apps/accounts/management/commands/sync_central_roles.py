import os
from collections import defaultdict

import psycopg
import psycopg.rows
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import connection, transaction

from apps.accounts.roles import FUNCTIONAL_ROLES

DEMO_ROLE_MAP = {
    "admin.fing@universidad.edu": {"superadmin"},
    "claudia.benitez@universidad.edu": {"decano"},
    "miguel.rojas@universidad.edu": {"coordinador"},
    "andres.molina@universidad.edu": {"docente"},
}

SECURITY_ROLE_MAP = {
    "administrativo": "administrativo",
    "docente": "docente",
    "estudiante": "estudiante",
    "coordinador": "coordinador",
    "decano": "decano",
    "superadmin": "superadmin",
}


class Command(BaseCommand):
    help = "Sincroniza roles funcionales en sga_central.auth_group/usuario_groups."

    def add_arguments(self, parser):
        mode = parser.add_mutually_exclusive_group(required=True)
        mode.add_argument("--dry-run", action="store_true")
        mode.add_argument("--apply", action="store_true")

    def handle(self, *args, **options):
        plan = self._build_plan()
        if options["dry_run"]:
            self._print_plan("DRY-RUN", plan)
            return

        with transaction.atomic():
            self._apply_plan(plan)

        self._print_plan("APPLY", plan)

    def _build_plan(self):
        user_model = get_user_model()
        users = list(user_model.objects.prefetch_related("groups").order_by("correo"))
        user_by_email = {user.correo: user for user in users}
        user_by_id = {user.id_usuario: user for user in users}
        current_groups = {
            user.correo: set(user.groups.values_list("name", flat=True))
            for user in users
        }
        existing_group_names = set(Group.objects.values_list("name", flat=True))

        role_sources = defaultdict(dict)
        self._collect_legacy_roles(user_by_email, role_sources)
        self._collect_security_roles(user_by_id, role_sources)
        self._collect_report_roles(user_by_email, user_by_id, role_sources)

        for user in users:
            if user.is_superuser:
                role_sources[user.correo]["superadmin"] = "is_superuser"

        for email, roles in DEMO_ROLE_MAP.items():
            if email in user_by_email:
                for role in roles:
                    role_sources[email][role] = "mapa demo explicito"

        assignments = []
        users_without_source = []
        unknown_existing_groups = sorted(
            {
                group
                for groups in current_groups.values()
                for group in groups
                if group not in FUNCTIONAL_ROLES
            }
        )

        for user in users:
            roles = set(role_sources.get(user.correo, {}))
            missing_roles = sorted(roles - current_groups[user.correo])
            for role in missing_roles:
                assignments.append(
                    {
                        "email": user.correo,
                        "role": role,
                        "source": role_sources[user.correo][role],
                    }
                )
            if not roles and not current_groups[user.correo]:
                users_without_source.append(user.correo)

        return {
            "total_users": len(users),
            "groups_before": sorted(existing_group_names),
            "groups_to_create": sorted(set(FUNCTIONAL_ROLES) - existing_group_names),
            "users_without_group_before": sum(
                1 for groups in current_groups.values() if not groups
            ),
            "assignments": assignments,
            "users_without_source": users_without_source,
            "unknown_existing_groups": unknown_existing_groups,
            "applied": {
                "groups_created": 0,
                "relations_created": 0,
            },
        }

    def _collect_legacy_roles(self, user_by_email, role_sources):
        try:
            with self._legacy_connection() as legacy:
                with legacy.cursor() as cursor:
                    cursor.execute(
                        """
                        select u.correo, g.name
                        from public.usuario_groups ug
                        join public.usuario u on u.id_usuario = ug.customuser_id
                        join public.auth_group g on g.id = ug.group_id
                        """
                    )
                    rows = list(cursor.fetchall())
        except psycopg.Error:
            return

        for row in rows:
            email = row["correo"]
            role = row["name"]
            if email in user_by_email and role in FUNCTIONAL_ROLES:
                role_sources[email][role] = "gestion_academica_local.usuario_groups"

    def _legacy_connection(self):
        return psycopg.connect(
            dbname=os.getenv("LEGACY_POSTGRES_DB", "gestion_academica_local"),
            user=os.getenv(
                "LEGACY_POSTGRES_USER",
                os.getenv("POSTGRES_USER", "postgres"),
            ),
            password=os.getenv(
                "LEGACY_POSTGRES_PASSWORD",
                os.getenv("POSTGRES_PASSWORD", "postgres"),
            ),
            host=os.getenv(
                "LEGACY_POSTGRES_HOST",
                os.getenv("POSTGRES_HOST", "localhost"),
            ),
            port=os.getenv("LEGACY_POSTGRES_PORT", os.getenv("POSTGRES_PORT", "5432")),
            sslmode=os.getenv(
                "LEGACY_POSTGRES_SSLMODE",
                os.getenv("POSTGRES_SSLMODE", "prefer"),
            ),
            row_factory=psycopg.rows.dict_row,
        )

    def _collect_security_roles(self, user_by_id, role_sources):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select ur.id_usuario, r.nombre_rol
                from seguridad.usuario_rol ur
                join seguridad.rol r on r.id_rol = ur.id_rol
                """
            )
            rows = cursor.fetchall()

        for user_id, role_name in rows:
            user = user_by_id.get(user_id)
            normalized = SECURITY_ROLE_MAP.get(str(role_name).lower())
            if user and normalized:
                role_sources[user.correo][normalized] = "seguridad.usuario_rol"

    def _collect_report_roles(self, user_by_email, user_by_id, role_sources):
        for email in self._emails_from_report_view("vw_estudiantes_detalle"):
            if email in user_by_email:
                role_sources[email]["estudiante"] = "reportes.vw_estudiantes_detalle"

        for email in self._emails_from_report_view("vw_profesores_detalle"):
            if email in user_by_email:
                role_sources[email]["docente"] = "reportes.vw_profesores_detalle"

        self._collect_report_user_id_roles(
            "vw_administrativos_global",
            "id_usuario",
            "administrativo",
            user_by_id,
            role_sources,
        )

        professor_roles = {
            row["id_profesor"]: row["correo"]
            for row in self._rows_from_report_view(
                "vw_profesores_detalle",
                "id_profesor, correo",
            )
        }
        for view_name, id_column, role in (
            ("vw_coordinadores_global", "id_profesor", "coordinador"),
            ("vw_decanos_global", "id_profesor", "decano"),
        ):
            for row in self._rows_from_report_view(view_name, id_column):
                email = professor_roles.get(row[id_column])
                if email in user_by_email:
                    role_sources[email][role] = f"reportes.{view_name}"

    def _emails_from_report_view(self, view_name):
        return [
            row["correo"]
            for row in self._rows_from_report_view(view_name, "correo")
            if row["correo"]
        ]

    def _collect_report_user_id_roles(
        self,
        view_name,
        id_column,
        role,
        user_by_id,
        role_sources,
    ):
        for row in self._rows_from_report_view(view_name, id_column):
            user = user_by_id.get(row[id_column])
            if user:
                role_sources[user.correo][role] = f"reportes.{view_name}"

    def _rows_from_report_view(self, view_name, columns):
        with connection.cursor() as cursor:
            cursor.execute(f'select {columns} from reportes."{view_name}"')
            column_names = [column[0] for column in cursor.description]
            return [
                dict(zip(column_names, row, strict=True))
                for row in cursor.fetchall()
            ]

    def _apply_plan(self, plan):
        for group_name in plan["groups_to_create"]:
            _, created = Group.objects.get_or_create(name=group_name)
            if created:
                plan["applied"]["groups_created"] += 1

        group_ids = dict(Group.objects.values_list("name", "id"))
        user_model = get_user_model()
        user_ids = dict(user_model.objects.values_list("correo", "id_usuario"))

        through = user_model.groups.through
        for assignment in plan["assignments"]:
            _, created = through.objects.get_or_create(
                customuser_id=user_ids[assignment["email"]],
                group_id=group_ids[assignment["role"]],
            )
            if created:
                plan["applied"]["relations_created"] += 1

    def _print_plan(self, prefix, plan):
        self.stdout.write(f"{prefix}: usuarios totales: {plan['total_users']}")
        self.stdout.write(
            f"{prefix}: grupos existentes antes: {', '.join(plan['groups_before'])}"
        )
        self.stdout.write(
            f"{prefix}: grupos por crear: {len(plan['groups_to_create'])}"
        )
        self.stdout.write(
            f"{prefix}: usuarios sin grupo antes: "
            f"{plan['users_without_group_before']}"
        )
        self.stdout.write(
            f"{prefix}: relaciones por crear: {len(plan['assignments'])}"
        )
        self.stdout.write(
            f"{prefix}: usuarios sin fuente de rol: "
            f"{len(plan['users_without_source'])}"
        )
        if plan["unknown_existing_groups"]:
            self.stdout.write(
                f"{prefix}: grupos no reconocidos: "
                f"{', '.join(plan['unknown_existing_groups'])}"
            )
        for assignment in plan["assignments"]:
            self.stdout.write(
                f"ASIGNAR: {assignment['email']} -> {assignment['role']} "
                f"({assignment['source']})"
            )
        for email in plan["users_without_source"]:
            self.stdout.write(f"SIN_FUENTE: {email}")
        if prefix == "APPLY":
            self.stdout.write(
                f"APPLY: grupos creados: {plan['applied']['groups_created']}"
            )
            self.stdout.write(
                f"APPLY: relaciones creadas: {plan['applied']['relations_created']}"
            )
