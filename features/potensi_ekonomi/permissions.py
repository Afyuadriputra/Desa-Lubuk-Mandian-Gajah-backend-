# features/potensi_ekonomi/permissions.py

from toolbox.security.auth import is_active_user
from toolbox.security.permissions import can_manage_bumdes as toolbox_can_manage_bumdes


def can_manage_data_bumdes(actor) -> bool:
    """Super Admin, Admin Desa, dan Admin BUMDes diizinkan mengelola."""
    return toolbox_can_manage_bumdes(actor)


def can_view_katalog_publik(actor) -> bool:
    """Semua warga yang aktif bisa melihat katalog wisata/usaha."""
    return is_active_user(actor)