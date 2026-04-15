# toolbox/security/auth.py

ROLE_SUPERADMIN = "SUPERADMIN"
ROLE_ADMIN = "ADMIN"
ROLE_BUMDES = "BUMDES"
ROLE_WARGA = "WARGA"

INTERNAL_ADMIN_ROLES = {ROLE_SUPERADMIN, ROLE_ADMIN}
BUMDES_ADMIN_ROLES = {ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_BUMDES}


def is_authenticated_user(user) -> bool:
    return bool(user and getattr(user, "is_authenticated", False))


def is_active_user(user) -> bool:
    return is_authenticated_user(user) and getattr(user, "is_active", False)


def get_user_role(user) -> str | None:
    if not is_authenticated_user(user):
        return None
    return getattr(user, "role", None)


def has_role(user, role: str) -> bool:
    return is_active_user(user) and get_user_role(user) == role


def has_any_role(user, roles: set[str] | list[str] | tuple[str, ...]) -> bool:
    return is_active_user(user) and get_user_role(user) in roles


def is_superadmin(user) -> bool:
    return has_role(user, ROLE_SUPERADMIN)


def is_admin_desa(user) -> bool:
    return has_role(user, ROLE_ADMIN)


def is_admin_bumdes(user) -> bool:
    return has_role(user, ROLE_BUMDES)


def is_warga(user) -> bool:
    return has_role(user, ROLE_WARGA)


def is_internal_admin(user) -> bool:
    return has_any_role(user, INTERNAL_ADMIN_ROLES)


def can_manage_bumdes(user) -> bool:
    return has_any_role(user, BUMDES_ADMIN_ROLES)