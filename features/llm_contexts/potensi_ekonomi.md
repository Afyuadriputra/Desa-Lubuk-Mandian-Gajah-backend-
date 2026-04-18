# Feature Context: potensi_ekonomi

Generated at: 2026-04-18T23:18:05
Feature path: `D:\Kuliah\joki\radit\desa\backend\features\potensi_ekonomi`

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


class PotensiEkonomiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'features.potensi_ekonomi'
```

---

## File: `models.py`

```python
# features/potensi_ekonomi/models.py

from django.db import models
from django.utils import timezone

from features.potensi_ekonomi.domain import VALID_KATEGORI
from toolbox.storage.paths import bumdes_media_upload_path


class BumdesUnitUsaha(models.Model):
    KATEGORI_CHOICES = [(k, k) for k in VALID_KATEGORI]

    id = models.BigAutoField(primary_key=True)
    nama_usaha = models.CharField(max_length=150)
    kategori = models.CharField(max_length=50, choices=KATEGORI_CHOICES)
    deskripsi = models.TextField()
    fasilitas = models.TextField(blank=True, null=True)  # Tambahan sesuai fitur PRD
    kontak_wa = models.CharField(max_length=20, blank=True, null=True)
    harga_tiket = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    foto_utama = models.ImageField(
        upload_to=bumdes_media_upload_path, 
        blank=True, 
        null=True
    )
    
    is_published = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bumdes_unit_usaha"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.nama_usaha} ({self.kategori})"
```

---

## File: `domain.py`

```python
# features/potensi_ekonomi/domain.py

KATEGORI_KOPERASI = "KOPERASI"
KATEGORI_WISATA = "WISATA"
KATEGORI_JASA = "JASA"

VALID_KATEGORI = {
    KATEGORI_KOPERASI,
    KATEGORI_WISATA,
    KATEGORI_JASA,
}

class PotensiEkonomiError(Exception):
    """Base exception untuk domain potensi ekonomi."""

class InvalidKategoriError(PotensiEkonomiError):
    """Kategori unit usaha tidak valid."""

class InvalidInputError(PotensiEkonomiError):
    """Input deskripsi atau kontak tidak valid."""

def validate_kategori(kategori: str) -> None:
    if kategori not in VALID_KATEGORI:
        raise InvalidKategoriError(f"Kategori '{kategori}' tidak valid.")

def validate_input_usaha(nama_usaha: str, kontak_wa: str) -> None:
    if not nama_usaha or len(str(nama_usaha).strip()) < 3:
        raise InvalidInputError("Nama usaha wajib diisi (minimal 3 karakter).")
    
    if kontak_wa:
        cleaned_wa = str(kontak_wa).replace("+", "").replace("-", "").strip()
        if not cleaned_wa.isdigit():
            raise InvalidInputError("Kontak WA hanya boleh berisi angka (dan tanda +).")
```

---

## File: `repositories.py`

```python
# features/potensi_ekonomi/repositories.py

from django.db.models import QuerySet
from features.potensi_ekonomi.models import BumdesUnitUsaha


class UnitUsahaRepository:
    def get_by_id(self, unit_id) -> BumdesUnitUsaha | None:
        return BumdesUnitUsaha.objects.filter(id=unit_id).first()

    def list_published(self) -> QuerySet[BumdesUnitUsaha]:
        return BumdesUnitUsaha.objects.filter(is_published=True)

    def list_all(self) -> QuerySet[BumdesUnitUsaha]:
        return BumdesUnitUsaha.objects.all()

    def create_unit(self, data: dict) -> BumdesUnitUsaha:
        return BumdesUnitUsaha.objects.create(**data)

    def update_unit(self, unit: BumdesUnitUsaha, data: dict) -> BumdesUnitUsaha:
        for field, value in data.items():
            setattr(unit, field, value)
        unit.save()
        return unit
        
    def delete_unit(self, unit: BumdesUnitUsaha) -> None:
        unit.delete()
```

---

## File: `services.py`

```python
# features/potensi_ekonomi/services.py

from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from features.potensi_ekonomi.domain import (
    PotensiEkonomiError,
    validate_input_usaha,
    validate_kategori,
)
from features.potensi_ekonomi.models import BumdesUnitUsaha
from features.potensi_ekonomi.permissions import (
    can_manage_data_bumdes,
    can_view_katalog_publik,
)
from features.potensi_ekonomi.repositories import UnitUsahaRepository
from toolbox.logging import audit_event, get_logger
from toolbox.security.upload_validators import validate_image_upload
# Import sanitize_rich_text_content dihapus karena sudah ditangani otomatis oleh Schema Ninja.


class PermissionDeniedError(Exception):
    pass

class UnitUsahaNotFoundError(Exception):
    pass

class FileUploadError(Exception):
    pass


class PotensiEkonomiService:
    def __init__(self, repository: UnitUsahaRepository | None = None):
        self.repository = repository or UnitUsahaRepository()
        self.logger = get_logger("features.potensi_ekonomi.services")

    def buat_unit_usaha(self, actor, data: dict, foto=None) -> BumdesUnitUsaha:
        if not can_manage_data_bumdes(actor):
            raise PermissionDeniedError("Anda tidak memiliki izin mengelola data BUMDes.")

        # Validasi domain (business rules) tetap berjalan
        validate_kategori(data.get("kategori"))
        validate_input_usaha(data.get("nama_usaha"), data.get("kontak_wa", ""))

        if foto:
            try:
                validate_image_upload(foto)
            except ValidationError as e:
                raise FileUploadError(str(e.message))

        # KISS & DRY: Dictionary 'data' dari API Pydantic/Ninja sudah terjamin 
        # tipe datanya (boolean, float) dan bersih dari XSS (SafeHTMLString).
        create_data = {
            "nama_usaha": data.get("nama_usaha"),
            "kategori": data.get("kategori"),
            "deskripsi": data.get("deskripsi"),
            "fasilitas": data.get("fasilitas"),
            "kontak_wa": data.get("kontak_wa"),
            "harga_tiket": data.get("harga_tiket"),
            "is_published": data.get("is_published", False),
        }
        
        if foto:
            create_data["foto_utama"] = foto

        unit = self.repository.create_unit(create_data)

        audit_event(
            action="BUMDES_UNIT_CREATED",
            actor_id=actor.id,
            actor_role=actor.role,
            target="bumdes_unit_usaha",
            target_id=unit.id,
            metadata={"nama_usaha": unit.nama_usaha}
        )

        return unit

    def get_katalog_publik(self, actor) -> QuerySet[BumdesUnitUsaha]:
        """Menampilkan data untuk warga (hanya yang is_published=True)."""
        if not can_view_katalog_publik(actor):
            raise PermissionDeniedError("Akses ditolak.")
        return self.repository.list_published()

    def get_semua_unit_admin(self, actor) -> QuerySet[BumdesUnitUsaha]:
        """Menampilkan semua data untuk admin (termasuk draft)."""
        if not can_manage_data_bumdes(actor):
            raise PermissionDeniedError("Akses ditolak.")
        return self.repository.list_all()

    def get_detail_unit(self, actor, unit_id: int) -> BumdesUnitUsaha:
        unit = self.repository.get_by_id(unit_id)
        if not unit:
            raise UnitUsahaNotFoundError("Data unit usaha tidak ditemukan.")

        # Warga biasa tidak boleh melihat data yang belum dipublish
        if not can_manage_data_bumdes(actor) and not unit.is_published:
             raise PermissionDeniedError("Data ini belum tersedia untuk publik.")

        return unit
```

---

## File: `permissions.py`

```python
# features/potensi_ekonomi/permissions.py

from toolbox.security.auth import is_active_user
from toolbox.security.permissions import can_manage_bumdes as toolbox_can_manage_bumdes


def can_manage_data_bumdes(actor) -> bool:
    """Super Admin, Admin Desa, dan Admin BUMDes diizinkan mengelola."""
    return toolbox_can_manage_bumdes(actor)


def can_view_katalog_publik(actor) -> bool:
    """Semua warga yang aktif bisa melihat katalog wisata/usaha."""
    return is_active_user(actor)
```

---

## File: `schemas.py`

```python
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
```

---

## File: `api.py`

```python
# features/potensi_ekonomi/api.py

from typing import List
from ninja import Router, Form, File
from ninja.files import UploadedFile

from .schemas import (
    BuatUnitUsahaIn, 
    KatalogPublikOut, 
    KatalogAdminOut, 
    UnitUsahaDetailOut
)
from .services import PotensiEkonomiService
from toolbox.api.auth import AuthActiveUser

router = Router(tags=["Potensi Ekonomi (BUMDes & Wisata)"])

# Dependency Inversion Principle
ekonomi_service = PotensiEkonomiService()


@router.get("/katalog", auth=AuthActiveUser, response=List[KatalogPublikOut])
def katalog_publik_api(request):
    """Endpoint untuk warga melihat etalase aktif."""
    return ekonomi_service.get_katalog_publik(request.user)


@router.get("/admin/list", auth=AuthActiveUser, response=List[KatalogAdminOut])
def list_admin_api(request):
    """
    Endpoint untuk Admin melihat semua data (termasuk Draft).
    Izin spesifik (can_manage_bumdes) sudah dijaga oleh Service Layer.
    """
    return ekonomi_service.get_semua_unit_admin(request.user)


@router.get("/{unit_id}", auth=AuthActiveUser, response=UnitUsahaDetailOut)
def detail_unit_api(request, unit_id: int):
    """Detail spesifik BUMDes/Wisata."""
    return ekonomi_service.get_detail_unit(request.user, unit_id)


@router.post("/admin/buat", auth=AuthActiveUser, response={201: KatalogAdminOut})
def buat_unit_usaha_api(
    request, 
    payload: Form[BuatUnitUsahaIn], 
    foto_utama: File[UploadedFile] = None
):
    """
    Endpoint untuk membuat Unit Usaha baru.
    Menerima Multipart/Form-Data karena ada gambar.
    Input HTML dari payload.deskripsi sudah otomatis bersih dari XSS oleh Schema.
    """
    unit = ekonomi_service.buat_unit_usaha(
        actor=request.user,
        data=payload.dict(), # Langsung diubah menjadi dictionary untuk service
        foto=foto_utama
    )
    return 201, unit
```

---
