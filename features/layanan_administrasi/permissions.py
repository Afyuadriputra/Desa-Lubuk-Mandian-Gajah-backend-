# features/layanan_administrasi/permissions.py

"""
Layer: Permissions

Tanggung jawab:
- Menentukan apakah actor boleh melakukan aksi tertentu.
- Tidak melakukan query database.
- Tidak memproses business flow.
"""

from toolbox.security.auth import is_active_user, is_warga
from toolbox.security.permissions import can_process_surat, can_view_all_surat


def can_submit_surat(actor) -> bool:
    """Hanya warga aktif yang bisa mengajukan surat."""
    return is_active_user(actor) and is_warga(actor)


def can_view_surat_detail(actor, surat) -> bool:
    """Warga hanya bisa melihat suratnya sendiri, admin bisa melihat semua."""
    if not is_active_user(actor):
        return False

    if can_view_all_surat(actor):
        return True

    return str(surat.pemohon_id) == str(actor.id)


def can_update_surat_status(actor) -> bool:
    """Hanya internal admin yang bisa memproses status surat."""
    return can_process_surat(actor)


def can_manage_template_surat(actor) -> bool:
    """
    Hanya admin/internal yang bisa mengelola template surat.

    Untuk KISS:
    - Kita reuse permission proses surat.
    - Jika nanti role template manager berbeda, baru pisahkan permission-nya.
    """
    return can_process_surat(actor)