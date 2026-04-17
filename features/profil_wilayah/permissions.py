# features/profil_wilayah/permissions.py

from toolbox.security.auth import is_active_user
from toolbox.security.permissions import can_manage_wilayah

def can_manage_data_wilayah(actor) -> bool:
    """Hanya Admin Desa dan Super Admin yang bisa mengelola."""
    return can_manage_wilayah(actor)

def can_view_data_publik(actor) -> bool:
    """Semua warga (bahkan mungkin publik tanpa login) bisa melihat profil desa."""
    return True # Untuk MVP, akses baca dibuat terbuka/publik