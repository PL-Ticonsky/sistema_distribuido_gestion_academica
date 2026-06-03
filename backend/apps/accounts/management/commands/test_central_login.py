from django.contrib.auth import authenticate, get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Prueba autenticacion central sin imprimir passwords."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--password", required=True)

    def handle(self, *args, **options):
        email = options["email"]
        password = options["password"]
        user_model = get_user_model()

        try:
            user = user_model.objects.get(correo=email)
        except user_model.DoesNotExist:
            self.stdout.write(f"FAIL: usuario inexistente: {email}")
            return

        if not user.is_active:
            self.stdout.write(f"FAIL: usuario inactivo: {email}")
            return

        authenticated_user = authenticate(username=email, password=password)
        if authenticated_user is None:
            self.stdout.write(f"FAIL: no autentica: {email}")
            return

        self.stdout.write(f"OK: autentica: {email}")
