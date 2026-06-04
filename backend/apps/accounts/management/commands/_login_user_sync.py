from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import connection, transaction

DEMO_PASSWORD = "Demo12345*"


class LoginUserSyncMixin:
    entity_label = "usuarios"
    entity_label_singular = "usuario"

    def add_mode_arguments(self, parser):
        mode = parser.add_mutually_exclusive_group(required=True)
        mode.add_argument(
            "--dry-run",
            action="store_true",
            help="Calcula los cambios sin escribir en la base de datos.",
        )
        mode.add_argument(
            "--apply",
            action="store_true",
            help="Aplica los cambios en public.usuario y usuario_groups.",
        )
        parser.add_argument(
            "--reset-password",
            action="store_true",
            help="Asigna la password demo a los usuarios sincronizados.",
        )

    def run_sync(self, options):
        plan = self._build_plan(reset_password=options["reset_password"])

        if options["dry_run"]:
            self._print_summary("DRY-RUN", plan)
            return

        with transaction.atomic():
            self._apply_plan(plan)

        self._print_summary("APPLY", plan)

    def _build_plan(self, reset_password):
        source_rows = self._read_source_rows()
        prepared_rows = self._prepare_rows(source_rows)
        user_model = get_user_model()
        users = list(user_model.objects.prefetch_related("groups").order_by("correo"))
        users_by_email = {self._normalize_email(user.correo): user for user in users}
        users_by_id = {user.id_usuario: user for user in users}
        current_roles_by_user_id = {
            user.id_usuario: {group.name for group in user.groups.all()}
            for user in users
        }
        required_roles = sorted(
            {role for row in prepared_rows for role in row["roles"]}
        )
        existing_groups = set(Group.objects.values_list("name", flat=True))

        seen_emails = set()
        users_to_create = []
        users_to_update = []
        users_omitted = []

        for row in prepared_rows:
            email = self._normalize_email(row["correo"])
            if not email:
                users_omitted.append(
                    {
                        "correo": "(sin correo)",
                        "reason": f"fila de {self.entity_label_singular} sin correo",
                    }
                )
                continue

            if email in seen_emails:
                users_omitted.append(
                    {
                        "correo": email,
                        "reason": f"correo duplicado en fuente de {self.entity_label}",
                    }
                )
                continue
            seen_emails.add(email)

            if not row["id_usuario"]:
                users_omitted.append(
                    {
                        "correo": email,
                        "reason": (
                            f"fila de {self.entity_label_singular} sin id_usuario"
                        ),
                    }
                )
                continue

            existing_by_email = users_by_email.get(email)
            existing_by_id = users_by_id.get(row["id_usuario"])
            if existing_by_id and existing_by_id.correo != email:
                users_omitted.append(
                    {
                        "correo": email,
                        "reason": (
                            "id_usuario ya existe con otro correo en public.usuario"
                        ),
                    }
                )
                continue

            if existing_by_email:
                current_roles = current_roles_by_user_id.get(
                    existing_by_email.id_usuario,
                    set(),
                )
                users_to_update.append(
                    {
                        "row": row,
                        "user": existing_by_email,
                        "roles_to_create": sorted(row["roles"] - current_roles),
                    }
                )
                continue

            if not row["tipo_de_documento"] or not row["numero_de_documento"]:
                users_omitted.append(
                    {
                        "correo": email,
                        "reason": "faltan tipo_de_documento o numero_de_documento",
                    }
                )
                continue

            users_to_create.append(
                {
                    "row": row,
                    "roles_to_create": sorted(row["roles"]),
                }
            )

        password_resets = (
            len(users_to_create) + len(users_to_update) if reset_password else 0
        )

        return {
            "source_found": len(source_rows),
            "prepared_found": len(prepared_rows),
            "required_roles": required_roles,
            "groups_to_create": sorted(set(required_roles) - existing_groups),
            "users_to_create": users_to_create,
            "users_to_update": users_to_update,
            "users_omitted": users_omitted,
            "relations_to_create": sum(
                len(item["roles_to_create"])
                for item in [*users_to_create, *users_to_update]
            ),
            "password_resets": password_resets,
            "reset_password": reset_password,
            "extra_counts": self._extra_counts(source_rows, prepared_rows),
            "applied": {
                "groups_created": 0,
                "users_created": 0,
                "users_updated": 0,
                "passwords_reset": 0,
                "relations_created": 0,
            },
        }

    def _prepare_rows(self, source_rows):
        prepared = {}
        omitted = []
        for row in source_rows:
            email = self._normalize_email(row["correo"])
            if not email:
                omitted.append(row)
                continue
            if email not in prepared:
                prepared[email] = {
                    **row,
                    "correo": email,
                    "roles": set(row["roles"]),
                }
                continue
            prepared[email]["roles"].update(row["roles"])
        return list(prepared.values()) + omitted

    def _apply_plan(self, plan):
        groups = {}
        for role in plan["required_roles"]:
            group, created = Group.objects.get_or_create(name=role)
            groups[role] = group
            if created:
                plan["applied"]["groups_created"] += 1

        user_model = get_user_model()

        for item in plan["users_to_create"]:
            row = item["row"]
            user = user_model(
                id_usuario=row["id_usuario"],
                correo=self._normalize_email(row["correo"]),
                nombre=row["nombre"] or self._normalize_email(row["correo"]),
                tipo_de_documento=row["tipo_de_documento"],
                numero_de_documento=row["numero_de_documento"],
                direccion=row["direccion"] or "",
                is_active=True,
                is_staff=False,
                is_superuser=False,
            )
            if plan["reset_password"]:
                user.set_password(DEMO_PASSWORD)
                plan["applied"]["passwords_reset"] += 1
            else:
                user.set_unusable_password()
            user.save()
            plan["applied"]["users_created"] += 1
            self._assign_groups(user, item["roles_to_create"], groups, plan)

        for item in plan["users_to_update"]:
            row = item["row"]
            user = item["user"]
            user.nombre = row["nombre"] or user.nombre
            user.is_active = True
            update_fields = ["nombre", "is_active"]

            if plan["reset_password"]:
                user.set_password(DEMO_PASSWORD)
                update_fields.append("password")
                plan["applied"]["passwords_reset"] += 1

            user.save(update_fields=update_fields)
            plan["applied"]["users_updated"] += 1
            self._assign_groups(user, item["roles_to_create"], groups, plan)

    def _assign_groups(self, user, roles, groups, plan):
        through = get_user_model().groups.through
        for role in roles:
            _, created = through.objects.get_or_create(
                customuser_id=user.id_usuario,
                group_id=groups[role].id,
            )
            if created:
                plan["applied"]["relations_created"] += 1

    def _normalize_email(self, email):
        return get_user_model().objects.normalize_email(email).strip() if email else ""

    def _view_exists(self, view_name):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select exists (
                    select 1
                    from information_schema.views
                    where table_schema = 'reportes'
                      and table_name = %s
                )
                """,
                [view_name],
            )
            return cursor.fetchone()[0]

    def _fetch_dicts(self, query, params=None):
        with connection.cursor() as cursor:
            cursor.execute(query, params or [])
            columns = [column[0] for column in cursor.description]
            return [
                dict(zip(columns, row, strict=True))
                for row in cursor.fetchall()
            ]

    def _extra_counts(self, source_rows, prepared_rows):
        return {}

    def _print_summary(self, prefix, plan):
        self.stdout.write(
            f"{prefix}: {self.entity_label} encontrados: {plan['source_found']}"
        )
        self.stdout.write(
            f"{prefix}: usuarios unicos procesables: {plan['prepared_found']}"
        )
        self.stdout.write(
            f"{prefix}: usuarios por crear: {len(plan['users_to_create'])}"
        )
        self.stdout.write(
            f"{prefix}: usuarios por actualizar: {len(plan['users_to_update'])}"
        )
        self.stdout.write(
            f"{prefix}: passwords por resetear: {plan['password_resets']}"
        )
        self.stdout.write(
            f"{prefix}: grupos por crear: {len(plan['groups_to_create'])}"
        )
        self.stdout.write(
            f"{prefix}: relaciones grupo por crear: {plan['relations_to_create']}"
        )
        self.stdout.write(
            f"{prefix}: usuarios omitidos: {len(plan['users_omitted'])}"
        )
        for label, value in plan["extra_counts"].items():
            self.stdout.write(f"{prefix}: {label}: {value}")

        if prefix == "APPLY":
            applied = plan["applied"]
            self.stdout.write(
                f"APPLY: grupos creados: {applied['groups_created']}"
            )
            self.stdout.write(
                f"APPLY: usuarios creados: {applied['users_created']}"
            )
            self.stdout.write(
                f"APPLY: usuarios actualizados: {applied['users_updated']}"
            )
            self.stdout.write(
                f"APPLY: passwords reseteados: {applied['passwords_reset']}"
            )
            self.stdout.write(
                f"APPLY: relaciones grupo creadas: "
                f"{applied['relations_created']}"
            )

        for omitted in plan["users_omitted"]:
            self.stdout.write(
                f"OMITIDO: {omitted['correo']} - {omitted['reason']}"
            )
