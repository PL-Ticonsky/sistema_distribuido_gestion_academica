from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.db import connection

from apps.accounts.models import CustomUser

USER_QUERY = """
    select
        p.id_usuario,
        p.nombre,
        p.tipo_de_documento,
        p.numero_de_documento,
        p.correo,
        p.direccion,
        c.password,
        c.last_login,
        c.is_superuser,
        c.is_staff,
        c.is_active,
        c.date_joined
    from personas.usuario_dato_personal p
    join seguridad.usuario_credencial c on c.id_usuario = p.id_usuario
    where {where_clause}
"""


def build_user(row):
    user = CustomUser(
        id_usuario=row[0],
        nombre=row[1],
        tipo_de_documento=row[2],
        numero_de_documento=row[3],
        correo=row[4],
        direccion=row[5],
        password=row[6],
        last_login=row[7],
        is_superuser=row[8],
        is_staff=row[9],
        is_active=row[10],
        date_joined=row[11],
    )
    user._state.adding = False
    user._state.db = "default"
    return user


class CentralSecurityBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        correo = username or kwargs.get("correo")
        if not correo or not password:
            return None

        with connection.cursor() as cursor:
            cursor.execute(
                USER_QUERY.format(where_clause="lower(p.correo) = lower(%s)"),
                [correo],
            )
            row = cursor.fetchone()

        if row is None or not row[10] or not check_password(password, row[6]):
            return None

        return build_user(row)

    def get_user(self, user_id):
        with connection.cursor() as cursor:
            cursor.execute(
                USER_QUERY.format(where_clause="p.id_usuario = %s"),
                [user_id],
            )
            row = cursor.fetchone()

        if row is None or not row[10]:
            return None

        return build_user(row)
