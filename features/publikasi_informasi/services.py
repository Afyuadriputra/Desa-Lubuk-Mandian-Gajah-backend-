# features/publikasi_informasi/services.py

from django.utils import timezone
from features.publikasi_informasi.domain import (
    PublikasiError, validate_publikasi_input, STATUS_PUBLISHED
)
from features.publikasi_informasi.permissions import can_create_or_edit_publikasi
from features.publikasi_informasi.repositories import PublikasiRepository
from toolbox.logging import audit_event
from toolbox.security.sanitizers import sanitize_html, sanitize_plain_text

class PublikasiAccessError(Exception):
    pass


class PublikasiNotFoundError(PublikasiError):
    pass

class PublikasiService:
    def __init__(self, repo: PublikasiRepository = None):
        self.repo = repo or PublikasiRepository()

    def buat_publikasi(self, actor, judul: str, konten_html: str, jenis: str, status: str):
        if not can_create_or_edit_publikasi(actor):
            raise PublikasiAccessError("Anda tidak memiliki izin mengelola publikasi.")

        judul = sanitize_plain_text(judul)
        konten_html = sanitize_html(konten_html)
        validate_publikasi_input(judul, konten_html, jenis, status)

        published_at = timezone.now() if status == STATUS_PUBLISHED else None

        publikasi = self.repo.create({
            "judul": judul,
            "konten_html": konten_html,
            "jenis": jenis,
            "status": status,
            "penulis_id": actor.id,
            "published_at": published_at
        })

        audit_event("PUBLIKASI_CREATED", actor_id=actor.id, target_id=publikasi.id, metadata={"jenis": jenis})
        return publikasi

    def ubah_status(self, actor, slug: str, new_status: str):
        if not can_create_or_edit_publikasi(actor):
            raise PublikasiAccessError("Akses ditolak.")
            
        publikasi = self.repo.get_by_slug(slug)
        if not publikasi:
            raise PublikasiError("Publikasi tidak ditemukan.")

        published_at = timezone.now() if new_status == STATUS_PUBLISHED else None
        updated = self.repo.update_status(publikasi, new_status, published_at)
        
        audit_event("PUBLIKASI_STATUS_UPDATED", actor_id=actor.id, target_id=updated.id, metadata={"new_status": new_status})
        return updated

    def ubah_publikasi(self, actor, slug: str, judul: str, konten_html: str, jenis: str, status: str):
        if not can_create_or_edit_publikasi(actor):
            raise PublikasiAccessError("Anda tidak memiliki izin mengelola publikasi.")

        publikasi = self.repo.get_by_slug(slug)
        if not publikasi:
            raise PublikasiError("Publikasi tidak ditemukan.")

        judul = sanitize_plain_text(judul)
        konten_html = sanitize_html(konten_html)
        validate_publikasi_input(judul, konten_html, jenis, status)

        published_at = timezone.now() if status == STATUS_PUBLISHED else None
        updated = self.repo.update_content(
            publikasi,
            {
                "judul": judul,
                "konten_html": konten_html,
                "jenis": jenis,
                "status": status,
                "published_at": published_at,
            },
        )
        audit_event("PUBLIKASI_UPDATED", actor_id=actor.id, target_id=updated.id, metadata={"slug": updated.slug})
        return updated

    def hapus_publikasi(self, actor, slug: str) -> None:
        if not can_create_or_edit_publikasi(actor):
            raise PublikasiAccessError("Anda tidak memiliki izin mengelola publikasi.")

        publikasi = self.repo.get_by_slug(slug)
        if not publikasi:
            raise PublikasiError("Publikasi tidak ditemukan.")

        target_id = publikasi.id
        self.repo.delete(publikasi)
        audit_event("PUBLIKASI_DELETED", actor_id=actor.id, target_id=target_id, metadata={"slug": slug})

    def get_publikasi_publik(self, jenis=None):
        """Hanya mengembalikan data yang berstatus PUBLISHED."""
        return self.repo.list_published(jenis=jenis)

    def get_detail_publik(self, slug: str):
        publikasi = self.repo.get_by_slug(slug)
        if not publikasi or publikasi.status != STATUS_PUBLISHED:
            raise PublikasiNotFoundError("Konten tidak ditemukan atau belum dipublikasikan.")
        return publikasi
