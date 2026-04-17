# features/publikasi_informasi/domain.py

STATUS_DRAFT = "DRAFT"
STATUS_PUBLISHED = "PUBLISHED"

JENIS_BERITA = "BERITA"
JENIS_PENGUMUMAN = "PENGUMUMAN"

VALID_STATUS = {STATUS_DRAFT, STATUS_PUBLISHED}
VALID_JENIS = {JENIS_BERITA, JENIS_PENGUMUMAN}


class PublikasiError(Exception):
    """Base exception untuk domain publikasi."""


def validate_publikasi_input(judul: str, konten_html: str, jenis: str, status: str) -> None:
    if not judul or len(str(judul).strip()) < 5:
        raise PublikasiError("Judul terlalu pendek (minimal 5 karakter).")
    
    if not konten_html or len(str(konten_html).strip()) < 10:
        raise PublikasiError("Konten tidak boleh kosong atau terlalu pendek.")
        
    if jenis not in VALID_JENIS:
        raise PublikasiError(f"Jenis publikasi '{jenis}' tidak dikenali.")
        
    if status not in VALID_STATUS:
        raise PublikasiError(f"Status '{status}' tidak valid.")