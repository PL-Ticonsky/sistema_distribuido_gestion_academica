from django.core.management.base import BaseCommand

from ._login_user_sync import LoginUserSyncMixin


class Command(LoginUserSyncMixin, BaseCommand):
    help = (
        "Sincroniza docentes academicos de reportes.vw_profesores_detalle "
        "hacia public.usuario como usuarios de login."
    )
    entity_label = "docentes"
    entity_label_singular = "docente"

    def add_arguments(self, parser):
        self.add_mode_arguments(parser)

    def handle(self, *args, **options):
        self.run_sync(options)

    def _read_source_rows(self):
        rows = self._fetch_dicts(
            """
            select
                p.id_usuario,
                p.profesor as nombre,
                p.correo,
                u.tipo_de_documento,
                u.numero_de_documento,
                u.direccion
            from reportes.vw_profesores_detalle p
            left join reportes.vw_usuarios_global u
                on u.id_usuario = p.id_usuario
            order by p.correo
            """
        )
        for row in rows:
            row["roles"] = {"docente"}
        return rows
