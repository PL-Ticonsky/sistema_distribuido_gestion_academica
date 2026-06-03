import logging
import uuid

from django.db import DatabaseError, connection, transaction
from django.utils import timezone

logger = logging.getLogger(__name__)

SENSITIVE_TOKENS = (
    "password",
    "contrasena",
    "contraseña",
    "hash",
    "token",
    "secret",
)


def _login_user_id(usuario):
    if not getattr(usuario, "is_authenticated", False):
        return None
    return getattr(usuario, "pk", None)


def _safe_text(value, max_length):
    text = str(value or "")
    lowered = text.lower()
    if any(token in lowered for token in SENSITIVE_TOKENS):
        return "[redactado]"
    return text[:max_length]


def _audit_user_id(cursor, usuario):
    login_id = _login_user_id(usuario)
    if login_id is None:
        return None

    cursor.execute(
        """
        select id_usuario
        from personas.usuario_dato_personal
        where id_usuario = %s
        """,
        [login_id],
    )
    row = cursor.fetchone()
    if row is not None:
        return row[0]

    correo = getattr(usuario, "correo", None)
    tipo_documento = getattr(usuario, "tipo_de_documento", None)
    numero_documento = getattr(usuario, "numero_de_documento", None)

    if correo:
        cursor.execute(
            """
            select id_usuario
            from personas.usuario_dato_personal
            where correo = %s
            """,
            [correo],
        )
        row = cursor.fetchone()
        if row is not None:
            return row[0]

    if tipo_documento and numero_documento:
        cursor.execute(
            """
            select id_usuario
            from personas.usuario_dato_personal
            where tipo_de_documento = %s
              and numero_de_documento = %s
            """,
            [tipo_documento, numero_documento],
        )
        row = cursor.fetchone()
        if row is not None:
            return row[0]

    return None


def registrar_auditoria(
    usuario,
    accion,
    descripcion,
    *,
    esquema_afectado=None,
    tabla_afectada=None,
):
    try:
        with transaction.atomic(savepoint=True):
            with connection.cursor() as cursor:
                id_usuario = _audit_user_id(cursor, usuario)
                if id_usuario is None:
                    logger.info("Auditoria omitida: usuario sin id compatible.")
                    return False
                cursor.execute(
                    """
                    insert into auditoria.auditoria (
                        id_auditoria,
                        id_usuario,
                        esquema_afectado,
                        tabla_afectada,
                        accion_realizada,
                        fecha_hora,
                        descripcion
                    )
                    values (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    [
                        uuid.uuid4(),
                        id_usuario,
                        _safe_text(esquema_afectado, 80) or None,
                        _safe_text(tabla_afectada, 80) or None,
                        _safe_text(accion, 100),
                        timezone.now(),
                        _safe_text(descripcion, 255) or None,
                    ],
                )
        return True
    except DatabaseError:
        logger.exception("No se pudo registrar auditoria.")
        return False
