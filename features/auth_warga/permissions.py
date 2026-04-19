# features/auth_warga/permissions.py

from features.auth_warga.domain import (
    ROLE_ADMIN,
    ROLE_BUMDES,
    ROLE_SUPERADMIN,
)
from toolbox.security.auth import is_active_user
from toolbox.security.permissions import (
    can_manage_admin_accounts,
    can_manage_warga_accounts,
)


ADMIN_SIDE_ROLES = {
    ROLE_SUPERADMIN,
    ROLE_ADMIN,
    ROLE_BUMDES,
}


def can_view_self(actor, target_user) -> bool:
    return is_active_user(actor) and str(actor.id) == str(target_user.id)


def can_activate_user(actor, target_user) -> bool:
    if target_user.role in ADMIN_SIDE_ROLES:
        return can_manage_admin_accounts(actor)
    return can_manage_warga_accounts(actor)


def can_deactivate_user(actor, target_user) -> bool:
    if str(actor.id) == str(target_user.id):
        return False

    if target_user.role in ADMIN_SIDE_ROLES:
        return can_manage_admin_accounts(actor)
    return can_manage_warga_accounts(actor)


def can_create_admin_user(actor) -> bool:
    return can_manage_admin_accounts(actor)


def can_create_warga_user(actor) -> bool:
    return can_manage_warga_accounts(actor)


def can_list_users(actor) -> bool:
    return can_manage_warga_accounts(actor)
