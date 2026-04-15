# toolbox/security/permissions.py

from toolbox.security.auth import (
    is_active_user,
    is_internal_admin,
    is_superadmin,
    can_manage_bumdes as _can_manage_bumdes,
)


def is_resource_owner(user, owner_id) -> bool:
    if not is_active_user(user):
        return False
    return str(getattr(user, "id", "")) == str(owner_id)


def can_view_own_resource(user, owner_id) -> bool:
    return is_resource_owner(user, owner_id)


def can_view_all_surat(user) -> bool:
    return is_internal_admin(user)


def can_process_surat(user) -> bool:
    return is_internal_admin(user)


def can_view_all_pengaduan(user) -> bool:
    return is_internal_admin(user)


def can_handle_pengaduan(user) -> bool:
    return is_internal_admin(user)


def can_manage_publikasi(user) -> bool:
    return is_internal_admin(user)


def can_manage_wilayah(user) -> bool:
    return is_internal_admin(user)


def can_manage_bumdes(user) -> bool:
    return _can_manage_bumdes(user)


def can_manage_admin_accounts(user) -> bool:
    return is_superadmin(user)


def can_manage_warga_accounts(user) -> bool:
    return is_internal_admin(user)