from typing import List, Optional
from ninja import Schema, Field
from toolbox.security.sanitizers import SafeHTMLString, SafePlainTextString


class TambahDusunIn(Schema):
    nama_dusun: SafePlainTextString
    kepala_dusun: SafePlainTextString


class UpdateDusunIn(Schema):
    nama_dusun: SafePlainTextString
    kepala_dusun: SafePlainTextString


class TambahPerangkatIn(Schema):
    user_id: str
    jabatan: SafePlainTextString
    is_published: bool = False


class UpdatePerangkatIn(Schema):
    user_id: str
    jabatan: SafePlainTextString
    is_published: bool = False


class UpdateProfilDesaIn(Schema):
    visi: SafeHTMLString
    misi: SafeHTMLString
    sejarah: SafeHTMLString


class DusunOut(Schema):
    id: int
    nama_dusun: str
    kepala_dusun: str


class PerangkatAdminOut(Schema):
    id: int
    user_id: str
    jabatan: str
    is_published: bool
    foto_url: Optional[str] = None

    @staticmethod
    def resolve_foto_url(obj):
        return obj.foto.url if obj.foto else None


class PerangkatPublikOut(Schema):
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
    profil: ProfilDesaOut
    perangkat: List[PerangkatPublikOut]