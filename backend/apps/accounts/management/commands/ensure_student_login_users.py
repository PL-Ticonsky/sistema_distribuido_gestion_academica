from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import connection, transaction

DEMO_PASSWORD = "Demo12345*"
STUDENT_ROLE = "estudiante"


class Command(BaseCommand):
    help = (
        "Sincroniza estudiantes academicos de reportes.vw_estudiantes_detalle "
        "hacia public.usuario como usuarios de login."
    )

    def add_arguments(self, parser):
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
            help="Asigna la password demo a los estudiantes sincronizados.",
        )

    def handle(self, *args, **options):
        plan = self._build_plan(reset_password=options["reset_password"])

        if options["dry_run"]:
            self._print_summary("DRY-RUN", plan)
            return

        with transaction.atomic():
            self._apply_plan(plan)

        self._print_summary("APPLY", plan)

    def _build_plan(self, reset_password):
        student_rows = self._read_student_rows()
        user_model = get_user_model()
        users = list(user_model.objects.prefetch_related("groups").order_by("correo"))
        users_by_email = {self._normalize_email(user.correo): user for user in users}
        users_by_id = {user.id_usuario: user for user in users}
        current_student_ids = {
            user.id_usuario
            for user in users
            if any(group.name == STUDENT_ROLE for group in user.groups.all())
        }

        existing_group = Group.objects.filter(name=STUDENT_ROLE).first()
        seen_emails = set()
        users_to_create = []
        users_to_update = []
        users_omitted = []

        for row in student_rows:
            email = self._normalize_email(row["correo"])
            if not email:
                users_omitted.append(
                    {
                        "correo": "(sin correo)",
                        "reason": "fila academica sin correo",
                    }
                )
                continue

            if email in seen_emails:
                users_omitted.append(
                    {
                        "correo": email,
                        "reason": "correo duplicado en reportes.vw_estudiantes_detalle",
                    }
                )
                continue
            seen_emails.add(email)

            if not row["id_usuario"]:
                users_omitted.append(
                    {
                        "correo": email,
                        "reason": "fila academica sin id_usuario",
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
                users_to_update.append(
                    {
                        "row": row,
                        "user": existing_by_email,
                        "needs_student_group": existing_by_email.id_usuario
                        not in current_student_ids,
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
                    "needs_student_group": True,
                }
            )

        relations_to_create = sum(
            1
            for item in [*users_to_create, *users_to_update]
            if item["needs_student_group"]
        )
        password_resets = (
            len(users_to_create) + len(users_to_update) if reset_password else 0
        )

        return {
            "students_found": len(student_rows),
            "users_to_create": users_to_create,
            "users_to_update": users_to_update,
            "users_omitted": users_omitted,
            "student_group_exists": existing_group is not None,
            "student_group_created": 0,
            "relations_to_create": relations_to_create,
            "password_resets": password_resets,
            "reset_password": reset_password,
            "applied": {
                "users_created": 0,
                "users_updated": 0,
                "passwords_reset": 0,
                "relations_created": 0,
            },
        }

    def _read_student_rows(self):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select
                    e.id_usuario,
                    e.estudiante,
                    e.correo,
                    u.tipo_de_documento,
                    u.numero_de_documento,
                    u.direccion
                from reportes.vw_estudiantes_detalle e
                left join reportes.vw_usuarios_global u
                    on u.id_usuario = e.id_usuario
                order by e.correo
                """
            )
            columns = [column[0] for column in cursor.description]
            return [
                dict(zip(columns, row, strict=True))
                for row in cursor.fetchall()
            ]

    def _apply_plan(self, plan):
        group, created = Group.objects.get_or_create(name=STUDENT_ROLE)
        if created:
            plan["student_group_created"] = 1

        user_model = get_user_model()

        for item in plan["users_to_create"]:
            row = item["row"]
            user = user_model(
                id_usuario=row["id_usuario"],
                correo=self._normalize_email(row["correo"]),
                nombre=row["estudiante"] or self._normalize_email(row["correo"]),
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
            self._assign_student_group(user, group, plan)

        for item in plan["users_to_update"]:
            row = item["row"]
            user = item["user"]
            user.nombre = row["estudiante"] or user.nombre
            user.is_active = True
            update_fields = ["nombre", "is_active"]

            if plan["reset_password"]:
                user.set_password(DEMO_PASSWORD)
                update_fields.append("password")
                plan["applied"]["passwords_reset"] += 1

            user.save(update_fields=update_fields)
            plan["applied"]["users_updated"] += 1
            self._assign_student_group(user, group, plan)

    def _assign_student_group(self, user, group, plan):
        through = get_user_model().groups.through
        _, created = through.objects.get_or_create(
            customuser_id=user.id_usuario,
            group_id=group.id,
        )
        if created:
            plan["applied"]["relations_created"] += 1

    def _normalize_email(self, email):
        return get_user_model().objects.normalize_email(email).strip() if email else ""

    def _print_summary(self, prefix, plan):
        self.stdout.write(
            f"{prefix}: estudiantes encontrados: {plan['students_found']}"
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
            f"{prefix}: grupo estudiante existente: {plan['student_group_exists']}"
        )
        self.stdout.write(
            f"{prefix}: relaciones grupo estudiante por crear: "
            f"{plan['relations_to_create']}"
        )
        self.stdout.write(
            f"{prefix}: usuarios omitidos: {len(plan['users_omitted'])}"
        )

        if prefix == "APPLY":
            applied = plan["applied"]
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
                f"APPLY: grupo estudiante creado: {plan['student_group_created']}"
            )
            self.stdout.write(
                "APPLY: relaciones grupo estudiante creadas: "
                f"{applied['relations_created']}"
            )

        for omitted in plan["users_omitted"]:
            self.stdout.write(
                f"OMITIDO: {omitted['correo']} - {omitted['reason']}"
            )
