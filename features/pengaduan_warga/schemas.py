# features/pengaduan_warga/schemas.py

from datetime import datetime
from typing import List, Optional
from ninja import Schema, Field
from toolbox.security.sanitizers import SafePlainTextString

# --- INPUT SCHEMAS ---

class BuatPengaduanIn(Schema):
    """Schema untuk input form-data (bukan JSON)"""
    kategori: str
    judul: SafePlainTextString
    deskripsi: SafePlainTextString

class ProsesPengaduanIn(Schema):
    """Schema untuk update status oleh Admin (JSON)"""
    status: str
    notes: Optional[SafePlainTextString] = None

# --- OUTPUT SCHEMAS ---

class PengaduanHistoryOut(Schema):
    status_to: str
    notes: Optional[str]
    # Otomatis ambil dari relasi changed_by.nama_lengkap, default "System" jika None
    changed_by_nama: str = Field("System", alias="changed_by.nama_lengkap")
    created_at: datetime

class PengaduanListOut(Schema):
    """Schema ringkas untuk daftar pengaduan (YAGNI: tidak perlu detail lengkap)"""
    id: int
    judul: str
    kategori: str
    status: str
    pelapor_nama: str = Field(..., alias="pelapor.nama_lengkap")
    created_at: datetime

class PengaduanDetailOut(Schema):
    """Schema lengkap untuk detail pengaduan beserta historinya"""
    id: int
    kategori: str
    judul: str
    deskripsi: str
    status: str
    foto_bukti_url: Optional[str] = None
    pelapor_nama: str = Field(..., alias="pelapor.nama_lengkap")
    histori: List[PengaduanHistoryOut] = []
    created_at: datetime
    updated_at: datetime

    # DRY: Method resolver bawaan Ninja untuk mengisi data custom
    @staticmethod
    def resolve_foto_bukti_url(obj):
        return obj.foto_bukti.url if obj.foto_bukti else None

    @staticmethod
    def resolve_histori(obj):
        # Mengambil semua histori yang terelasi secara otomatis
        return list(obj.histori_tindak_lanjut.all())