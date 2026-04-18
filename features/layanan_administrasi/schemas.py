# features/layanan_administrasi/schemas.py
from ninja import Schema
from datetime import datetime
from uuid import UUID
from typing import List, Optional

class SuratIn(Schema):
    jenis_surat: str
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
    pdf_url: Optional[str] = None

    @staticmethod
    def resolve_pdf_url(obj):
        return obj.pdf_file.url if obj.pdf_file else None


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
    notes: str = None
    nomor_surat: str = None
    rejection_reason: str = None
