import os

import psycopg
import psycopg.rows
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

USER_COLUMNS = (
    "id_usuario",
    "password",
    "last_login",
    "is_superuser",
    "is_staff",
    "is_active",
    "date_joined",
    "nombre",
    "tipo_de_documento",
    "numero_de_documento",
    "correo",
    "direccion",
)


class Command(BaseCommand):
    help = (
        "Sincroniza usuarios y grupos desde gestion_academica_local hacia "
        "sga_central sin imprimir contrasenas ni hashes."
    )

    def add_arguments(self, parser):
        mode = parser.add_mutually_exclusive_group(required=True)
        mode.add_argument(
            "--dry-run",
            action="store_true",
            help="Calcula cambios sin escribir en sga_central.",
        )
        mode.add_argument(
            "--apply",
            action="store_true",
            help="Aplica la sincronizacion en sga_central.",
        )

    def handle(self, *args, **options):
        legacy_data = self._read_legacy_data()
        plan = self._build_plan(legacy_data)

        if options["dry_run"]:
            self._print_summary(plan, prefix="DRY-RUN")
            return

        with transaction.atomic():
            self._apply_plan(plan)

        self._print_summary(plan, prefix="APPLY")

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

    def _read_legacy_data(self):
        with self._legacy_connection() as legacy:
            with legacy.cursor() as cursor:
                self._validate_legacy_user_columns(cursor)
                user_columns = ", ".join(USER_COLUMNS)
                cursor.execute(
                    f"select {user_columns} from public.usuario order by correo"
                )
                users = list(cursor.fetchall())

                cursor.execute(
                    """
                    select id, name
                    from public.auth_group
                    order by id
                    """
                )
                groups = list(cursor.fetchall())

                cursor.execute(
                    """
                    select ug.customuser_id as user_id, g.name as group_name
                    from public.usuario_groups ug
                    join public.auth_group g on g.id = ug.group_id
                    order by g.name
                    """
                )
                user_groups = list(cursor.fetchall())

                cursor.execute(
                    """
                    select customuser_id as user_id, permission_id
                    from public.usuario_user_permissions
                    order by customuser_id, permission_id
                    """
                )
                user_permissions = list(cursor.fetchall())

        return {
            "users": users,
            "groups": groups,
            "user_groups": user_groups,
            "user_permissions": user_permissions,
        }

    def _validate_legacy_user_columns(self, cursor):
        cursor.execute(
            """
            select column_name
            from information_schema.columns
            where table_schema = 'public' and table_name = 'usuario'
            """
        )
        columns = {row["column_name"] for row in cursor.fetchall()}
        missing = sorted(set(USER_COLUMNS) - columns)
        if missing:
            raise CommandError(
                "La tabla legacy public.usuario no tiene las columnas esperadas: "
                + ", ".join(missing)
            )

    def _build_plan(self, legacy_data):
        user_model = get_user_model()
        central_users = list(user_model.objects.all())
        central_by_email = {user.correo: user for user in central_users}
        central_by_id = {user.id_usuario: user for user in central_users}

        users_to_create = []
        users_to_update = []
        users_omitted = []

        for legacy_user in legacy_data["users"]:
            legacy_id = legacy_user["id_usuario"]
            legacy_email = legacy_user["correo"]
            existing_by_email = central_by_email.get(legacy_email)
            existing_by_id = central_by_id.get(legacy_id)

            if existing_by_id and existing_by_id.correo != legacy_email:
                users_omitted.append(
                    {
                        "correo": legacy_email,
                        "reason": "id_usuario ya existe con otro correo en sga_central",
                    }
                )
                continue

            if existing_by_email:
                users_to_update.append(
                    {
                        "legacy": legacy_user,
                        "central_id": existing_by_email.id_usuario,
                    }
                )
            else:
                users_to_create.append(legacy_user)

        legacy_group_names = {group["name"] for group in legacy_data["groups"]}
        central_group_names = set(Group.objects.values_list("name", flat=True))
        groups_to_create = sorted(legacy_group_names - central_group_names)

        target_user_ids = {
            row["id_usuario"] for row in users_to_create
        } | {row["legacy"]["id_usuario"] for row in users_to_update}
        source_user_ids = {row["id_usuario"] for row in legacy_data["users"]}
        target_group_names = legacy_group_names | central_group_names

        user_groups_to_copy = [
            row
            for row in legacy_data["user_groups"]
            if row["user_id"] in source_user_ids
            and row["group_name"] in target_group_names
        ]

        available_permission_ids = set(Permission.objects.values_list("id", flat=True))
        user_permissions_to_copy = [
            row
            for row in legacy_data["user_permissions"]
            if row["user_id"] in target_user_ids
            and row["permission_id"] in available_permission_ids
        ]
        incompatible_permissions = len(legacy_data["user_permissions"]) - len(
            user_permissions_to_copy
        )

        return {
            "legacy_users": len(legacy_data["users"]),
            "central_users_before": len(central_users),
            "users_to_create": users_to_create,
            "users_to_update": users_to_update,
            "users_omitted": users_omitted,
            "groups_to_create": groups_to_create,
            "user_groups_to_copy": user_groups_to_copy,
            "user_permissions_to_copy": user_permissions_to_copy,
            "incompatible_permissions": incompatible_permissions,
            "applied": {
                "users_created": 0,
                "users_updated": 0,
                "groups_created": 0,
                "user_groups_copied": 0,
                "user_permissions_copied": 0,
            },
        }

    def _apply_plan(self, plan):
        user_model = get_user_model()

        for group_name in plan["groups_to_create"]:
            _, created = Group.objects.get_or_create(name=group_name)
            if created:
                plan["applied"]["groups_created"] += 1

        for legacy_user in plan["users_to_create"]:
            user_model.objects.create(**self._user_kwargs(legacy_user))
            plan["applied"]["users_created"] += 1

        for update_item in plan["users_to_update"]:
            legacy_user = update_item["legacy"]
            central_id = update_item["central_id"]
            if central_id != legacy_user["id_usuario"]:
                self._delete_existing_m2m(central_id)
                self._update_user_primary_key(legacy_user["correo"], legacy_user)
            else:
                user_model.objects.filter(id_usuario=legacy_user["id_usuario"]).update(
                    **self._user_kwargs(legacy_user)
                )
            plan["applied"]["users_updated"] += 1

        group_ids = dict(Group.objects.values_list("name", "id"))
        for relation in plan["user_groups_to_copy"]:
            group_id = group_ids.get(relation["group_name"])
            if group_id is None:
                continue
            inserted = self._insert_m2m(
                "usuario_groups",
                relation["user_id"],
                "group_id",
                group_id,
            )
            plan["applied"]["user_groups_copied"] += inserted

        for relation in plan["user_permissions_to_copy"]:
            inserted = self._insert_m2m(
                "usuario_user_permissions",
                relation["user_id"],
                "permission_id",
                relation["permission_id"],
            )
            plan["applied"]["user_permissions_copied"] += inserted

    def _user_kwargs(self, legacy_user):
        return {column: legacy_user[column] for column in USER_COLUMNS}

    def _delete_existing_m2m(self, central_id):
        with connection.cursor() as cursor:
            cursor.execute(
                "delete from public.usuario_groups where customuser_id = %s",
                [central_id],
            )
            cursor.execute(
                "delete from public.usuario_user_permissions where customuser_id = %s",
                [central_id],
            )

    def _update_user_primary_key(self, correo, legacy_user):
        assignments = ", ".join(f"{column} = %s" for column in USER_COLUMNS)
        values = [legacy_user[column] for column in USER_COLUMNS]
        values.append(correo)
        with connection.cursor() as cursor:
            cursor.execute(
                f"update public.usuario set {assignments} where correo = %s",
                values,
            )

    def _insert_m2m(self, table_name, user_id, relation_column, relation_id):
        with connection.cursor() as cursor:
            cursor.execute(
                (
                    f"insert into public.{table_name} "
                    f"(customuser_id, {relation_column}) values (%s, %s) "
                    "on conflict do nothing"
                ),
                [user_id, relation_id],
            )
            return cursor.rowcount

    def _print_summary(self, plan, prefix):
        self.stdout.write(
            f"{prefix}: usuarios legacy encontrados: {plan['legacy_users']}"
        )
        self.stdout.write(
            f"{prefix}: usuarios existentes en sga_central antes: "
            f"{plan['central_users_before']}"
        )
        self.stdout.write(
            f"{prefix}: usuarios por crear: {len(plan['users_to_create'])}"
        )
        self.stdout.write(
            f"{prefix}: usuarios por actualizar: {len(plan['users_to_update'])}"
        )
        self.stdout.write(
            f"{prefix}: usuarios omitidos: {len(plan['users_omitted'])}"
        )
        self.stdout.write(
            f"{prefix}: grupos por crear: {len(plan['groups_to_create'])}"
        )
        self.stdout.write(
            f"{prefix}: relaciones usuario-grupo a copiar: "
            f"{len(plan['user_groups_to_copy'])}"
        )
        self.stdout.write(
            f"{prefix}: permisos directos a copiar: "
            f"{len(plan['user_permissions_to_copy'])}"
        )
        self.stdout.write(
            f"{prefix}: permisos directos incompatibles: "
            f"{plan['incompatible_permissions']}"
        )

        if prefix == "APPLY":
            applied = plan["applied"]
            self.stdout.write(f"APPLY: usuarios creados: {applied['users_created']}")
            self.stdout.write(
                f"APPLY: usuarios actualizados: {applied['users_updated']}"
            )
            self.stdout.write(f"APPLY: grupos creados: {applied['groups_created']}")
            self.stdout.write(
                "APPLY: relaciones usuario-grupo copiadas: "
                f"{applied['user_groups_copied']}"
            )
            self.stdout.write(
                "APPLY: permisos directos copiados: "
                f"{applied['user_permissions_copied']}"
            )

        for omitted in plan["users_omitted"]:
            self.stdout.write(
                f"OMITIDO: {omitted['correo']} - {omitted['reason']}"
            )
