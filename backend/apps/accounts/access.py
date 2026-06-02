from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect

from apps.accounts.roles import get_role_labels, get_user_roles

STRUCTURE_ROLES = ("coordinador", "decano", "superadmin")
FINANCIAL_ROLES = (
    "estudiante",
    "coordinador",
    "decano",
    "administrativo",
    "superadmin",
)
STUDENT_ROLES = ("estudiante", "coordinador", "decano", "superadmin")
TEACHING_ROLES = ("docente", "coordinador", "decano", "superadmin")
HOMOLOGATION_ROLES = (
    "estudiante",
    "docente",
    "coordinador",
    "decano",
    "superadmin",
)
INDICATOR_ROLES = (
    "estudiante",
    "docente",
    "coordinador",
    "decano",
    "superadmin",
)
AUDIT_ROLES = ("superadmin",)


def user_has_any_role(user, allowed_roles):
    roles = set(get_user_roles(user))
    return "superadmin" in roles or bool(roles.intersection(allowed_roles))


class RoleRequiredMixin(AccessMixin):
    allowed_roles = ()
    permission_denied_message = (
        "No tienes permisos para acceder a esta pantalla con tus roles actuales."
    )

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if user_has_any_role(request.user, self.allowed_roles):
            return super().dispatch(request, *args, **kwargs)

        roles = ", ".join(get_role_labels(request.user)) or "sin roles funcionales"
        messages.error(
            request,
            f"{self.permission_denied_message} Roles actuales: {roles}.",
        )
        return redirect("accounts:dashboard")
