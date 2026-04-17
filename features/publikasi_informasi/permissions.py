# features/publikasi_informasi/permissions.py

from toolbox.security.auth import is_active_user
from toolbox.security.permissions import can_manage_publikasi


def can_create_or_edit_publikasi(actor) -> bool:
    """Hanya Admin Desa dan Super Admin yang bisa menambah/mengedit publikasi."""
    return can_manage_publikasi(actor)


def can_view_publikasi_publik(actor) -> bool:
    """Semua warga (bahkan mungkin publik tanpa login) bisa melihat publikasi."""
    return True