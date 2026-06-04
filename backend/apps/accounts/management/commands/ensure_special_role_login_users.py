from django.core.management.base import BaseCommand

from ._login_user_sync import LoginUserSyncMixin

FDW_SCHEMAS = (
    "fdw_ingenieria",
    "fdw_ciencias_educacion",
    "fdw_tecnologica",
    "fdw_medio_ambiente",
    "fdw_artes",
)


class Command(LoginUserSyncMixin, BaseCommand):
    help = (
        "Sincroniza decanos y coordinadores hacia public.usuario como "
        "usuarios de login."
    )
    entity_label = "roles especiales"
    entity_label_singular = "rol especial"

    def add_arguments(self, parser):
        self.add_mode_arguments(parser)

    def handle(self, *args, **options):
        self.run_sync(options)

    def _read_source_rows(self):
        rows = []
        if self._view_exists("vw_decanos_global"):
            rows.extend(
                self._read_special_from_report_view("vw_decanos_global", "decano")
            )
        else:
            rows.extend(self._read_special_from_fdw_tables("decano"))

        if self._view_exists("vw_coordinadores_global"):
            rows.extend(
                self._read_special_from_report_view(
                    "vw_coordinadores_global",
                    "coordinador",
                )
            )
        else:
            rows.extend(self._read_special_from_fdw_tables("coordinador"))

        return rows

    def _read_special_from_report_view(self, view_name, role):
        rows = self._fetch_dicts(
            f"""
            select
                p.id_usuario,
                p.profesor as nombre,
                p.correo,
                u.tipo_de_documento,
                u.numero_de_documento,
                u.direccion,
                %s as special_role
            from reportes."{view_name}" s
            join reportes.vw_profesores_detalle p
                on p.id_profesor = s.id_profesor
            left join reportes.vw_usuarios_global u
                on u.id_usuario = p.id_usuario
            order by p.correo
            """,
            [role],
        )
        for row in rows:
            row["roles"] = {"docente", role}
        return rows

    def _read_special_from_fdw_tables(self, role):
        union_sql = "\nunion all\n".join(
            f"""
            select
                p.id_usuario,
                u.nombre,
                u.correo,
                u.tipo_de_documento,
                u.numero_de_documento,
                u.direccion,
                %s as special_role
            from {schema}.{role} s
            join {schema}.profesor p
                on p.id_profesor = s.id_profesor
            left join reportes.vw_usuarios_global u
                on u.id_usuario = p.id_usuario
            """
            for schema in FDW_SCHEMAS
        )
        rows = self._fetch_dicts(
            f"select * from ({union_sql}) special_rows order by correo",
            [role] * len(FDW_SCHEMAS),
        )
        for row in rows:
            row["roles"] = {"docente", role}
        return rows

    def _extra_counts(self, source_rows, prepared_rows):
        return {
            "decanos encontrados": sum(
                1 for row in source_rows if row["special_role"] == "decano"
            ),
            "coordinadores encontrados": sum(
                1 for row in source_rows if row["special_role"] == "coordinador"
            ),
        }
