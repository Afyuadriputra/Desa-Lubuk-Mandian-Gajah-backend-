# features/layanan_administrasi/schemas.py

"""
Layer: Schemas

Tanggung jawab:
- Mendefinisikan kontrak input/output API.
- Tidak berisi business logic.
- Resolver hanya untuk format response sederhana.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from ninja import Schema


# ============================================================
# Template Surat Schemas
# ============================================================

class TemplateSuratOut(Schema):
    id: int
    kode: str
    nama: str
    deskripsi: Optional[str] = None
    is_active: bool
    file_template_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_file_template_url(obj):
        return obj.file_template.url if obj.file_template else None


class TemplateSuratCreateIn(Schema):
    """
    Metadata untuk membuat template surat.

    Catatan:
    - File .docx tidak masuk schema ini.
    - File diterima lewat File(...) di api.py.
    """
    kode: str
    nama: str
    deskripsi: Optional[str] = None
    is_active: bool = True


class TemplateSuratUpdateIn(Schema):
    """
    Metadata untuk update template surat.

    Catatan:
    - Semua field optional agar admin bisa update sebagian data.
    - File template sebaiknya di-update lewat endpoint upload terpisah
      atau parameter File(...) di api.py.
    """
    nama: Optional[str] = None
    deskripsi: Optional[str] = None
    is_active: Optional[bool] = None


# ============================================================
# Surat Schemas
# ============================================================

class SuratIn(Schema):
    """
    Input pengajuan surat.

    Flow baru:
    - Gunakan template_id.

    Legacy:
    - jenis_surat masih disediakan agar kompatibel dengan flow lama.
    """
    template_id: Optional[int] = None
    jenis_surat: Optional[str] = None
    keperluan: str


class SuratHistoryOut(Schema):
    status_from: Optional[str] = None
    status_to: str
    notes: Optional[str] = None
    changed_by_nama: Optional[str] = None
    created_at: datetime

    @staticmethod
    def resolve_changed_by_nama(obj):
        if obj.changed_by:
            return obj.changed_by.nama_lengkap
        return None


class SuratOut(Schema):
    id: UUID
    jenis_surat: str
    status: str
    created_at: datetime

    template_id: Optional[int] = None
    template_nama: Optional[str] = None

    pdf_url: Optional[str] = None
    docx_url: Optional[str] = None

    @staticmethod
    def resolve_template_id(obj):
        return obj.template_id if obj.template_id else None

    @staticmethod
    def resolve_template_nama(obj):
        return obj.template.nama if obj.template else None

    @staticmethod
    def resolve_pdf_url(obj):
        return obj.pdf_file.url if obj.pdf_file else None

    @staticmethod
    def resolve_docx_url(obj):
        return obj.docx_file.url if obj.docx_file else None


class SuratDetailOut(SuratOut):
    keperluan: str
    nomor_surat: Optional[str] = None
    rejection_reason: Optional[str] = None
    updated_at: datetime
    histori: List[SuratHistoryOut] = []

    @staticmethod
    def resolve_histori(obj):
        return list(obj.histori_status.all())


class ProsesSuratIn(Schema):
    status: str
    notes: Optional[str] = None
    nomor_surat: Optional[str] = None
    rejection_reason: Optional[str] = None