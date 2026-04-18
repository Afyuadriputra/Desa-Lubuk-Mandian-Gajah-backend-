# features/profil_wilayah/schemas.py

from typing import List, Optional
from ninja import Schema, Field
from toolbox.security.sanitizers import SafeHTMLString, SafePlainTextString

# --- INPUT SCHEMAS ---

class TambahDusunIn(Schema):
    nama_dusun: SafePlainTextString
    kepala_dusun: SafePlainTextString

class TambahPerangkatIn(Schema):
    """Untuk form-data saat upload foto perangkat"""
    user_id: str
    jabatan: SafePlainTextString
    is_published: bool = False

class UpdateProfilDesaIn(Schema):
    """Asumsi menggunakan Rich Text Editor untuk Visi, Misi, Sejarah"""
    visi: SafeHTMLString
    misi: SafeHTMLString
    sejarah: SafeHTMLString


# --- OUTPUT SCHEMAS ---

class DusunOut(Schema):
    id: int
    nama_dusun: str
    kepala_dusun: str

class PerangkatPublikOut(Schema):
    """YAGNI: Publik hanya butuh nama, jabatan, dan foto"""
    jabatan: str
    nama: str = Field(..., alias="user.nama_lengkap")
    foto_url: Optional[str] = None

    @staticmethod
    def resolve_foto_url(obj):
        return obj.foto.url if obj.foto else None

class ProfilDesaOut(Schema):
    visi: str
    misi: str
    sejarah: str

class ProfilPublikAggregatedOut(Schema):
    """KISS: Menggabungkan Profil dan Perangkat dalam 1 endpoint untuk efisiensi Frontend"""
    profil: ProfilDesaOut
    perangkat: List[PerangkatPublikOut]