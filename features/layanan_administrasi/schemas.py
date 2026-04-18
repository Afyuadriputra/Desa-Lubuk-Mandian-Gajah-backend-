# features/layanan_administrasi/schemas.py
from ninja import Schema
from datetime import datetime
from uuid import UUID
from typing import List

class SuratIn(Schema):
    jenis_surat: str
    keperluan: str

class SuratOut(Schema):
    id: UUID
    jenis_surat: str
    status: str
    created_at: datetime
    pdf_url: str = None

class ProsesSuratIn(Schema):
    status: str
    notes: str = None
    nomor_surat: str = None
    rejection_reason: str = None