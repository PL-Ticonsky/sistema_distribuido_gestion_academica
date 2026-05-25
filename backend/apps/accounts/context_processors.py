from apps.accounts.roles import get_user_roles


def functional_roles(request):
    roles = set(get_user_roles(request.user))
    is_superadmin = "superadmin" in roles

    return {
        "condor_roles": roles,
        "condor_is_superadmin": is_superadmin,
        "condor_show_structure": is_superadmin
        or bool(roles.intersection({"coordinador", "decano"})),
        "condor_show_student": is_superadmin
        or bool(roles.intersection({"estudiante", "coordinador", "decano"})),
        "condor_show_teacher": is_superadmin
        or bool(roles.intersection({"docente", "coordinador", "decano"})),
        "condor_show_financial": is_superadmin
        or bool(
            roles.intersection(
                {"estudiante", "coordinador", "decano", "administrativo"},
            ),
        ),
        "condor_show_homologation": is_superadmin
        or bool(roles.intersection({"estudiante", "docente", "coordinador", "decano"})),
        "condor_show_audit": is_superadmin,
    }
