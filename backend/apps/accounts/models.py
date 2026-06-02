import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import connection, models
from django.utils import timezone

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    class TipoDocumento(models.TextChoices):
        CC = "CC", "Cedula de ciudadania"
        TI = "TI", "Tarjeta de identidad"
        CE = "CE", "Cedula de extranjeria"

    id_usuario = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    date_joined = models.DateTimeField(default=timezone.now)
    nombre = models.CharField(max_length=80)
    tipo_de_documento = models.CharField(
        max_length=2,
        choices=TipoDocumento.choices,
    )
    numero_de_documento = models.CharField(max_length=20)
    correo = models.EmailField(max_length=254, unique=True)
    direccion = models.CharField(max_length=120, blank=True, null=True)  # noqa: DJ001
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "correo"
    REQUIRED_FIELDS = ["nombre", "tipo_de_documento", "numero_de_documento"]

    class Meta:
        db_table = "usuario"
        managed = False
        constraints = [
            models.UniqueConstraint(
                fields=["tipo_de_documento", "numero_de_documento"],
                name="usuario_tipo_documento_numero_documento_uniq",
            ),
        ]

    def __str__(self):
        return f"{self.nombre} <{self.correo}>"

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")
        if update_fields and set(update_fields) == {"last_login"}:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    update seguridad.usuario_credencial
                    set last_login = %s
                    where id_usuario = %s
                    """,
                    [self.last_login, self.id_usuario],
                )
            return

        return super().save(*args, **kwargs)
