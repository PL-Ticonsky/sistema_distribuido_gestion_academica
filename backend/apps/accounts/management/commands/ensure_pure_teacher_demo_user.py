import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils import timezone

from apps.accounts.roles import FUNCTIONAL_ROLES

DEMO_EMAIL = "docente.puro.fing@universidad.edu"
DEMO_NAME = "Docente Puro Ingenieria"
DEMO_PASSWORD = "Demo12345*"
DEMO_DOCUMENT = "800000123"
DEMO_USER_ID = uuid.uuid5(uuid.NAMESPACE_DNS, DEMO_EMAIL)
DEMO_PROFESSOR_ID = uuid.uuid5(uuid.NAMESPACE_DNS, f"profesor:{DEMO_EMAIL}")
FACULTY_ID = "FING"
TEACHER_ROLE = "docente"


class Command(BaseCommand):
    help = (
        "Asegura un usuario demo docente puro con login central y registro "
        "academico en FING."
    )

    def add_arguments(self, parser):
        mode = parser.add_mutually_exclusive_group(required=True)
        mode.add_argument("--dry-run", action="store_true")
        mode.add_argument("--apply", action="store_true")
        parser.add_argument("--reset-password", action="store_true")

    def handle(self, *args, **options):
        plan = self._build_plan(reset_password=options["reset_password"])

        if options["dry_run"]:
            self._print_summary("DRY-RUN", plan)
            return

        with transaction.atomic():
            self._apply_plan(plan)

        self._print_summary("APPLY", plan)

    def _build_plan(self, reset_password):
        user_model = get_user_model()
        user = user_model.objects.filter(correo=DEMO_EMAIL).first()
        user_id = user.id_usuario if user is not None else DEMO_USER_ID
        current_roles = set()
        if user is not None:
            current_roles = set(user.groups.values_list("name", flat=True))
        extra_roles = sorted((current_roles & set(FUNCTIONAL_ROLES)) - {TEACHER_ROLE})
        return {
            "login_exists": user is not None,
            "user_id": user_id,
            "person_exists": self._exists(
                "personas",
                "usuario_dato_personal",
                "id_usuario",
                user_id,
            ),
            "credential_exists": self._exists(
                "seguridad",
                "usuario_credencial",
                "id_usuario",
                user_id,
            ),
            "professor_exists": self._exists(
                "fdw_ingenieria",
                "profesor",
                "id_profesor",
                DEMO_PROFESSOR_ID,
            ),
            "teacher_group_exists": Group.objects.filter(name=TEACHER_ROLE).exists(),
            "teacher_relation_exists": TEACHER_ROLE in current_roles,
            "extra_roles": extra_roles,
            "reset_password": reset_password,
            "applied": {
                "login_created": 0,
                "login_updated": 0,
                "persons_upserted": 0,
                "credentials_upserted": 0,
                "professors_upserted": 0,
                "groups_created": 0,
                "relations_created": 0,
                "extra_relations_removed": 0,
                "passwords_reset": 0,
            },
        }

    def _apply_plan(self, plan):
        group, created = Group.objects.get_or_create(name=TEACHER_ROLE)
        if created:
            plan["applied"]["groups_created"] += 1

        user_model = get_user_model()
        user = user_model.objects.filter(correo=DEMO_EMAIL).first()
        if user is None:
            user = user_model(
                id_usuario=plan["user_id"],
                correo=DEMO_EMAIL,
                nombre=DEMO_NAME,
                tipo_de_documento="CC",
                numero_de_documento=DEMO_DOCUMENT,
                direccion="",
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
            plan["applied"]["login_created"] += 1
        else:
            user.nombre = DEMO_NAME
            user.tipo_de_documento = "CC"
            user.numero_de_documento = DEMO_DOCUMENT
            user.is_active = True
            user.is_staff = False
            user.is_superuser = False
            update_fields = [
                "nombre",
                "tipo_de_documento",
                "numero_de_documento",
                "is_active",
                "is_staff",
                "is_superuser",
            ]
            if plan["reset_password"]:
                user.set_password(DEMO_PASSWORD)
                update_fields.append("password")
                plan["applied"]["passwords_reset"] += 1
            user.save(update_fields=update_fields)
            plan["applied"]["login_updated"] += 1

        self._upsert_central_person(plan["user_id"])
        plan["applied"]["persons_upserted"] += 1
        self._upsert_central_credentials(user)
        plan["applied"]["credentials_upserted"] += 1
        self._upsert_professor(plan["user_id"])
        plan["applied"]["professors_upserted"] += 1

        through = user_model.groups.through
        _, relation_created = through.objects.get_or_create(
            customuser_id=user.id_usuario,
            group_id=group.id,
        )
        if relation_created:
            plan["applied"]["relations_created"] += 1

        extra_groups = list(Group.objects.filter(name__in=plan["extra_roles"]))
        removed = user.groups.filter(
            id__in=[group.id for group in extra_groups],
        ).count()
        if extra_groups:
            user.groups.remove(*extra_groups)
        plan["applied"]["extra_relations_removed"] = removed

    def _upsert_central_person(self, user_id):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                insert into personas.usuario_dato_personal (
                    id_usuario,
                    nombre,
                    tipo_de_documento,
                    numero_de_documento,
                    correo,
                    direccion
                )
                values (%s, %s, %s, %s, %s, %s)
                on conflict (id_usuario) do update
                set nombre = excluded.nombre,
                    tipo_de_documento = excluded.tipo_de_documento,
                    numero_de_documento = excluded.numero_de_documento,
                    correo = excluded.correo,
                    direccion = excluded.direccion
                """,
                [
                    user_id,
                    DEMO_NAME,
                    "CC",
                    DEMO_DOCUMENT,
                    DEMO_EMAIL,
                    "",
                ],
            )

    def _upsert_central_credentials(self, user):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                insert into seguridad.usuario_credencial (
                    id_usuario,
                    password,
                    last_login,
                    is_superuser,
                    is_staff,
                    is_active,
                    date_joined
                )
                values (%s, %s, %s, false, false, true, %s)
                on conflict (id_usuario) do update
                set password = excluded.password,
                    is_superuser = false,
                    is_staff = false,
                    is_active = true
                """,
                [
                    user.id_usuario,
                    user.password,
                    None,
                    timezone.now(),
                ],
            )

    def _upsert_professor(self, user_id):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                update fdw_ingenieria.profesor
                set id_usuario = %s,
                    id_facultad = %s,
                    categoria = %s,
                    vinculacion = %s
                where id_profesor = %s
                """,
                [
                    user_id,
                    FACULTY_ID,
                    "Asistente",
                    "Planta",
                    DEMO_PROFESSOR_ID,
                ],
            )
            if cursor.rowcount:
                return

            cursor.execute(
                """
                insert into fdw_ingenieria.profesor (
                    id_profesor,
                    id_usuario,
                    id_facultad,
                    categoria,
                    vinculacion
                )
                values (%s, %s, %s, %s, %s)
                """,
                [
                    DEMO_PROFESSOR_ID,
                    user_id,
                    FACULTY_ID,
                    "Asistente",
                    "Planta",
                ],
            )

    def _exists(self, schema, table, column, value):
        with connection.cursor() as cursor:
            cursor.execute(
                (
                    f'select exists (select 1 from "{schema}"."{table}" '
                    f"where {column} = %s)"
                ),
                [value],
            )
            return cursor.fetchone()[0]

    def _print_summary(self, prefix, plan):
        self.stdout.write(f"{prefix}: login existente: {plan['login_exists']}")
        self.stdout.write(
            f"{prefix}: persona central existente: {plan['person_exists']}"
        )
        self.stdout.write(
            f"{prefix}: credencial central existente: {plan['credential_exists']}"
        )
        self.stdout.write(
            f"{prefix}: profesor academico existente: {plan['professor_exists']}"
        )
        self.stdout.write(
            f"{prefix}: grupo docente existente: {plan['teacher_group_exists']}"
        )
        self.stdout.write(
            f"{prefix}: relacion grupo docente existente: "
            f"{plan['teacher_relation_exists']}"
        )
        self.stdout.write(
            f"{prefix}: relaciones funcionales extra a remover: "
            f"{len(plan['extra_roles'])}"
        )
        self.stdout.write(
            f"{prefix}: passwords por resetear: {1 if plan['reset_password'] else 0}"
        )

        if prefix == "APPLY":
            for label, value in plan["applied"].items():
                self.stdout.write(f"APPLY: {label}: {value}")
