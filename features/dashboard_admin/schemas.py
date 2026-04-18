# features/dashboard_admin/schemas.py
from ninja import Schema
from typing import List, Dict, Any

class SummarySchema(Schema):
    total_warga_aktif: int
    surat_pending: int
    pengaduan_aktif: int
    bumdes_published: int

class StatItemSchema(Schema):
    # Field opsional karena key-nya bisa 'status' atau 'kategori'
    status: str = None
    kategori: str = None
    total: int

class DashboardChartSchema(Schema):
    surat_by_status: List[StatItemSchema]
    pengaduan_by_kategori: List[StatItemSchema]

class DashboardResponseSchema(Schema):
    data: Dict[str, Any] # Membungkus response dalam key "data"