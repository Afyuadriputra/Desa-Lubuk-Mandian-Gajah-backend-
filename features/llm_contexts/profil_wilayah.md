# Feature Context: profil_wilayah

Generated at: 2026-04-18T23:18:05
Feature path: `D:\Kuliah\joki\radit\desa\backend\features\profil_wilayah`

Dokumen ini berisi layer penting untuk konteks LLM.
Folder `tests`, `migrations`, `logs`, dan file non-konteks tidak disertakan.

## Included Layers

- `apps.py`
- `models.py`
- `domain.py`
- `repositories.py`
- `services.py`
- `permissions.py`
- `schemas.py`
- `api.py`

---

## File: `apps.py`

```python
from django.apps import AppConfig


class ProfilWilayahConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'features.profil_wilayah'
```

---

## File: `models.py`

```python
# features/profil_wilayah/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from toolbox.storage.paths import perangkat_photo_upload_path

class WilayahDusun(models.Model):
    id = models.BigAutoField(primary_key=True)
    nama_dusun = models.CharField(max_length=100)
    kepala_dusun = models.CharField(max_length=150)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "wilayah_dusun"


class WilayahPerangkat(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    jabatan = models.CharField(max_length=100)
    foto = models.ImageField(upload_to=perangkat_photo_upload_path, blank=True, null=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "wilayah_perangkat"


class ProfilDesa(models.Model):
    """YAGNI: Tabel singleton untuk menyimpan Visi, Misi, dan Sejarah"""
    visi = models.TextField()
    misi = models.TextField()
    sejarah = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "profil_desa"
```

---

## File: `domain.py`

```python
# features/profil_wilayah/domain.py

class ProfilWilayahError(Exception):
    """Base exception untuk domain profil wilayah."""

class InvalidDataError(ProfilWilayahError):
    """Data input tidak valid."""

def validate_dusun(nama_dusun: str, kepala_dusun: str) -> None:
    if not nama_dusun or len(str(nama_dusun).strip()) < 3:
        raise InvalidDataError("Nama dusun wajib diisi (minimal 3 karakter).")
    if not kepala_dusun or len(str(kepala_dusun).strip()) < 3:
        raise InvalidDataError("Nama kepala dusun wajib diisi.")

def validate_perangkat(jabatan: str) -> None:
    if not jabatan or len(str(jabatan).strip()) < 3:
        raise InvalidDataError("Jabatan wajib diisi.")

def validate_profil_desa(visi: str, misi: str, sejarah: str) -> None:
    if not visi or not misi or not sejarah:
        raise InvalidDataError("Visi, misi, dan sejarah tidak boleh kosong.")
```

---

## File: `repositories.py`

```python
# features/profil_wilayah/repositories.py

from features.profil_wilayah.models import WilayahDusun, WilayahPerangkat, ProfilDesa

class DusunRepository:
    def list_all(self):
        return WilayahDusun.objects.all()

    def create(self, nama_dusun: str, kepala_dusun: str) -> WilayahDusun:
        return WilayahDusun.objects.create(nama_dusun=nama_dusun, kepala_dusun=kepala_dusun)


class PerangkatRepository:
    def list_published(self):
        return WilayahPerangkat.objects.select_related("user").filter(is_published=True)

    def list_all(self):
        return WilayahPerangkat.objects.select_related("user").all()

    def create(self, user_id, jabatan: str, is_published: bool, foto=None) -> WilayahPerangkat:
        return WilayahPerangkat.objects.create(
            user_id=user_id, jabatan=jabatan, is_published=is_published, foto=foto
        )


class ProfilDesaRepository:
    def get_profil(self) -> ProfilDesa:
        profil, _ = ProfilDesa.objects.get_or_create(id=1, defaults={
            "visi": "Visi Desa", "misi": "Misi Desa", "sejarah": "Sejarah Desa"
        })
        return profil

    def update_profil(self, visi: str, misi: str, sejarah: str) -> ProfilDesa:
        profil = self.get_profil()
        profil.visi = visi
        profil.misi = misi
        profil.sejarah = sejarah
        profil.save()
        return profil
```

---

## File: `services.py`

```python
# features/profil_wilayah/services.py

from django.core.exceptions import ValidationError
from features.profil_wilayah.domain import validate_dusun, validate_perangkat, validate_profil_desa
from features.profil_wilayah.permissions import can_manage_data_wilayah
from features.profil_wilayah.repositories import DusunRepository, PerangkatRepository, ProfilDesaRepository
from toolbox.logging import audit_event
from toolbox.security.upload_validators import validate_image_upload

class ProfilWilayahAccessError(Exception):
    pass

class DusunService:
    def __init__(self, repo: DusunRepository = None):
        self.repo = repo or DusunRepository()

    def tambah_dusun(self, actor, nama_dusun: str, kepala_dusun: str):
        if not can_manage_data_wilayah(actor):
            raise ProfilWilayahAccessError("Akses ditolak.")
        validate_dusun(nama_dusun, kepala_dusun)
        dusun = self.repo.create(nama_dusun, kepala_dusun)
        audit_event("DUSUN_CREATED", actor_id=actor.id, target_id=dusun.id)
        return dusun

    def get_semua_dusun(self):
        return self.repo.list_all()


class PerangkatService:
    def __init__(self, repo: PerangkatRepository = None):
        self.repo = repo or PerangkatRepository()

    def tambah_perangkat(self, actor, user_id, jabatan: str, is_published: bool, foto=None):
        if not can_manage_data_wilayah(actor):
            raise ProfilWilayahAccessError("Akses ditolak.")
        validate_perangkat(jabatan)
        
        if foto:
            validate_image_upload(foto)

        perangkat = self.repo.create(user_id, jabatan, is_published, foto)
        audit_event("PERANGKAT_CREATED", actor_id=actor.id, target_id=perangkat.id)
        return perangkat

    def get_perangkat_publik(self):
        return self.repo.list_published()


class ProfilDesaService:
    def __init__(self, repo: ProfilDesaRepository = None):
        self.repo = repo or ProfilDesaRepository()

    # features/profil_wilayah/services.py
# Tidak perlu lagi mengimpor sanitize_html atau bleach di sini!

    def perbarui_profil(self, actor, visi: str, misi: str, sejarah: str):
        if not can_manage_data_wilayah(actor):
            raise ProfilWilayahAccessError("Akses ditolak.")
            
        # domain validation tetap berjalan
        validate_profil_desa(visi, misi, sejarah) 
        
        # Data visi, misi, sejarah sudah otomatis ter-sanitasi oleh Pydantic Schema!
        profil = self.repo.update_profil(visi, misi, sejarah)
        audit_event("PROFIL_DESA_UPDATED", actor_id=actor.id)
        return profil

    def get_profil(self):
        return self.repo.get_profil()
```

---

## File: `permissions.py`

```python
# features/profil_wilayah/permissions.py

from toolbox.security.auth import is_active_user
from toolbox.security.permissions import can_manage_wilayah

def can_manage_data_wilayah(actor) -> bool:
    """Hanya Admin Desa dan Super Admin yang bisa mengelola."""
    return can_manage_wilayah(actor)

def can_view_data_publik(actor) -> bool:
    """Semua warga (bahkan mungkin publik tanpa login) bisa melihat profil desa."""
    return True # Untuk MVP, akses baca dibuat terbuka/publik
```

---

## File: `schemas.py`

```python
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
```

---

## File: `api.py`

```python
# features/profil_wilayah/api.py

from ninja import Router, Form, File
from ninja.files import UploadedFile

from .schemas import (
    TambahDusunIn, 
    TambahPerangkatIn, 
    UpdateProfilDesaIn,
    DusunOut, 
    ProfilPublikAggregatedOut,
    ProfilDesaOut
)
from .services import DusunService, PerangkatService, ProfilDesaService
from toolbox.api.auth import AuthAdminOnly

router = Router(tags=["Profil Wilayah"])

# Dependency Inversion Principle (DIP)
dusun_service = DusunService()
perangkat_service = PerangkatService()
profil_service = ProfilDesaService()


@router.get("/publik", response=ProfilPublikAggregatedOut)
def profil_publik_api(request):
    """
    Endpoint terbuka tanpa Auth. 
    Menggabungkan Visi/Misi dan list Perangkat Desa dalam satu panggilan.
    """
    profil = profil_service.get_profil()
    perangkat = perangkat_service.get_perangkat_publik()
    
    return {
        "profil": profil,
        "perangkat": list(perangkat)
    }


@router.post("/admin/dusun", auth=AuthAdminOnly, response={201: DusunOut})
def tambah_dusun_api(request, payload: TambahDusunIn):
    """Hanya Admin/Superadmin yang bisa menambah dusun."""
    dusun = dusun_service.tambah_dusun(
        actor=request.user, 
        nama_dusun=payload.nama_dusun, 
        kepala_dusun=payload.kepala_dusun
    )
    return 201, dusun


@router.post("/admin/perangkat", auth=AuthAdminOnly, response={201: dict})
def tambah_perangkat_api(
    request, 
    payload: Form[TambahPerangkatIn], 
    foto: File[UploadedFile] = None
):
    """Menambah data perangkat desa beserta fotonya."""
    perangkat = perangkat_service.tambah_perangkat(
        actor=request.user,
        user_id=payload.user_id,
        jabatan=payload.jabatan,
        is_published=payload.is_published,
        foto=foto
    )
    return 201, {"detail": "Perangkat berhasil ditambahkan", "id": perangkat.id}


@router.put("/admin/profil", auth=AuthAdminOnly, response=ProfilDesaOut)
def update_profil_desa_api(request, payload: UpdateProfilDesaIn):
    """
    Update data Visi, Misi, dan Sejarah (Singleton).
    Input HTML aman karena menggunakan SafeHTMLString di schema.
    """
    profil = profil_service.perbarui_profil(
        actor=request.user,
        visi=payload.visi,
        misi=payload.misi,
        sejarah=payload.sejarah
    )
    return profil
```

---
