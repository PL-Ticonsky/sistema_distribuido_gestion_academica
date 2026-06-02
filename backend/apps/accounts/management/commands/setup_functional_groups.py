from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from apps.accounts.roles import FUNCTIONAL_ROLES


class Command(BaseCommand):
    help = "Crea los grupos funcionales iniciales de CONDOR 2."

    def handle(self, *args, **options):
        for role in FUNCTIONAL_ROLES:
            _, created = Group.objects.get_or_create(name=role)
            action = "creado" if created else "existente"
            self.stdout.write(f"Grupo {role}: {action}.")

        self.stdout.write(self.style.SUCCESS("Grupos funcionales listos."))
