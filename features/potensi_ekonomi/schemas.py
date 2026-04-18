# features/potensi_ekonomi/schemas.py

from datetime import datetime
from typing import Optional
from ninja import Schema
from toolbox.security.sanitizers import SafeHTMLString, SafePlainTextString

# --- INPUT SCHEMAS ---

class BuatUnitUsahaIn(Schema):
    """
    Schema untuk input form-data.
    DRY: SafePlainTextString dan SafeHTMLString otomatis membersihkan XSS!
    """
    nama_usaha: SafePlainTextString
    kategori: str
    deskripsi: SafeHTMLString
    fasilitas: Optional[SafeHTMLString] = None
    kontak_wa: Optional[str] = None
    harga_tiket: Optional[float] = None
    is_published: bool = False


class UpdateUnitUsahaIn(Schema):
    nama_usaha: SafePlainTextString
    kategori: str
    deskripsi: SafeHTMLString
    fasilitas: Optional[SafeHTMLString] = None
    kontak_wa: Optional[str] = None
    harga_tiket: Optional[float] = None
    is_published: bool = False

# --- OUTPUT SCHEMAS ---

class KatalogPublikOut(Schema):
    """YAGNI: Warga hanya butuh data dasar untuk melihat katalog."""
    id: int
    nama_usaha: str
    kategori: str
    deskripsi: str
    harga_tiket: Optional[float]
    foto_url: Optional[str] = None

    @staticmethod
    def resolve_foto_url(obj):
        return obj.foto_utama.url if obj.foto_utama else None

class KatalogAdminOut(Schema):
    """YAGNI: Admin butuh melihat status publish di tabel list dashboard."""
    id: int
    nama_usaha: str
    kategori: str
    is_published: bool
    created_at: datetime

class UnitUsahaDetailOut(Schema):
    """Schema lengkap untuk halaman detail."""
    id: int
    nama_usaha: str
    kategori: str
    deskripsi: str
    fasilitas: Optional[str]
    kontak_wa: Optional[str]
    harga_tiket: Optional[float]
    is_published: bool
    foto_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_foto_url(obj):
        return obj.foto_utama.url if obj.foto_utama else None
