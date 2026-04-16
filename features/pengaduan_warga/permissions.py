# features/pengaduan_warga/permissions.py

from toolbox.security.auth import is_active_user, is_warga
from toolbox.security.permissions import can_handle_pengaduan, can_view_all_pengaduan


def can_submit_pengaduan(actor) -> bool:
    return is_active_user(actor) and is_warga(actor)


def can_view_pengaduan_detail(actor, pengaduan) -> bool:
    if not is_active_user(actor):
        return False
    if can_view_all_pengaduan(actor):
        return True
    return str(pengaduan.pelapor_id) == str(actor.id)


def can_update_pengaduan_status(actor) -> bool:
    return can_handle_pengaduan(actor)