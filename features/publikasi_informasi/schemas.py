# features/publikasi_informasi/schemas.py

from datetime import datetime
from typing import Optional
from ninja import Schema, Field
from toolbox.security.sanitizers import SafeHTMLString, SafePlainTextString

# --- INPUT SCHEMAS ---

class BuatPublikasiIn(Schema):
    """
    DRY: SafePlainTextString dan SafeHTMLString otomatis membersihkan 
    input dari potensi XSS Attack saat request masuk.
    """
    judul: SafePlainTextString
    konten_html: SafeHTMLString
    jenis: str = "BERITA"
    status: str = "DRAFT"

class UbahStatusIn(Schema):
    status: str


class UpdatePublikasiIn(Schema):
    judul: SafePlainTextString
    konten_html: SafeHTMLString
    jenis: str
    status: str = "DRAFT"


# --- OUTPUT SCHEMAS ---

class PublikasiListOut(Schema):
    """
    YAGNI: Hanya mengirim data meta untuk card/daftar berita.
    Tidak perlu mengirim 'konten_html' di sini untuk menghemat bandwidth.
    """
    judul: str
    slug: str
    jenis: str
    penulis_nama: str = Field("Admin", alias="penulis.nama_lengkap")
    published_at: Optional[datetime] = None

class PublikasiDetailOut(Schema):
    """Schema lengkap untuk halaman baca artikel."""
    judul: str
    slug: str
    konten_html: str
    jenis: str
    status: str
    penulis_nama: str = Field("Admin", alias="penulis.nama_lengkap")
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
