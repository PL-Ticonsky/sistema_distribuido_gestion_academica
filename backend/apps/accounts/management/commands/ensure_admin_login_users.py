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
        "Sincroniza administrativos academicos hacia public.usuario como "
        "usuarios de login."
    )
    entity_label = "administrativos"
    entity_label_singular = "administrativo"

    def add_arguments(self, parser):
        self.add_mode_arguments(parser)

    def handle(self, *args, **options):
        self.run_sync(options)

    def _read_source_rows(self):
        if self._view_exists("vw_administrativos_global"):
            rows = self._read_from_report_view()
        else:
            rows = self._read_from_fdw_tables()

        for row in rows:
            row["roles"] = {"administrativo"}
        return rows

    def _read_from_report_view(self):
        return self._fetch_dicts(
            """
            select
                a.id_usuario,
                u.nombre,
                u.correo,
                u.tipo_de_documento,
                u.numero_de_documento,
                u.direccion
            from reportes.vw_administrativos_global a
            join reportes.vw_usuarios_global u
                on u.id_usuario = a.id_usuario
            order by u.correo
            """
        )

    def _read_from_fdw_tables(self):
        union_sql = "\nunion all\n".join(
            f"""
            select
                a.id_usuario,
                u.nombre,
                u.correo,
                u.tipo_de_documento,
                u.numero_de_documento,
                u.direccion
            from {schema}.administrativo a
            join reportes.vw_usuarios_global u
                on u.id_usuario = a.id_usuario
            """
            for schema in FDW_SCHEMAS
        )
        return self._fetch_dicts(
            f"select * from ({union_sql}) admin_rows order by correo"
        )
