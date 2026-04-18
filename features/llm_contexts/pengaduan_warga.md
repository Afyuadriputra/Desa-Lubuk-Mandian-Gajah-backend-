# Feature Context: pengaduan_warga

Generated at: 2026-04-18T23:18:05
Feature path: `D:\Kuliah\joki\radit\desa\backend\features\pengaduan_warga`

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


class PengaduanWargaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "features.pengaduan_warga"
```

---

## File: `models.py`

```python
# features/pengaduan_warga/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone

from features.pengaduan_warga.domain import STATUS_OPEN, VALID_STATUSES
from toolbox.storage.paths import pengaduan_bukti_upload_path


class LayananPengaduan(models.Model):
    STATUS_CHOICES = [(s, s) for s in VALID_STATUSES]

    # PRD meminta id SERIAL (integer auto-increment)
    id = models.BigAutoField(primary_key=True)
    pelapor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="pengaduan_dibuat"
    )
    kategori = models.CharField(max_length=50)
    judul = models.CharField(max_length=150)
    deskripsi = models.TextField()
    
    foto_bukti = models.ImageField(
        upload_to=pengaduan_bukti_upload_path, 
        blank=True, 
        null=True
    )
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default=STATUS_OPEN
    )
    
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "layanan_pengaduan"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.status}] {self.judul[:20]}... - {self.pelapor.nama_lengkap}"


class LayananPengaduanHistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    pengaduan = models.ForeignKey(
        LayananPengaduan, 
        on_delete=models.CASCADE, 
        related_name="histori_tindak_lanjut"
    )
    status_from = models.CharField(max_length=20, blank=True, null=True)
    status_to = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        db_table = "layanan_pengaduan_history"
        ordering = ["-created_at"]
```

---

## File: `domain.py`

```python
# features/pengaduan_warga/domain.py

STATUS_OPEN = "OPEN"
STATUS_TRIAGED = "TRIAGED"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_RESOLVED = "RESOLVED"
STATUS_CLOSED = "CLOSED"

VALID_STATUSES = {
    STATUS_OPEN,
    STATUS_TRIAGED,
    STATUS_IN_PROGRESS,
    STATUS_RESOLVED,
    STATUS_CLOSED,
}

# State Machine Pengaduan
VALID_TRANSITIONS = {
    STATUS_OPEN: {STATUS_TRIAGED, STATUS_CLOSED},  # Bisa langsung ditutup jika spam/invalid
    STATUS_TRIAGED: {STATUS_IN_PROGRESS, STATUS_CLOSED},
    STATUS_IN_PROGRESS: {STATUS_RESOLVED, STATUS_CLOSED},
    STATUS_RESOLVED: {STATUS_CLOSED},
    STATUS_CLOSED: set(),  # Terminal state
}

class PengaduanError(Exception):
    """Base exception untuk domain pengaduan."""

class InvalidStatusTransitionError(PengaduanError):
    """Transisi status tidak diizinkan."""

class NoteRequiredError(PengaduanError):
    """Catatan admin wajib diisi untuk tindakan ini."""

class InvalidInputError(PengaduanError):
    """Input judul, deskripsi, atau kategori tidak valid."""


def validate_pengaduan_input(kategori: str, judul: str, deskripsi: str) -> None:
    if not kategori or not str(kategori).strip():
        raise InvalidInputError("Kategori pengaduan wajib diisi.")
    if not judul or len(str(judul).strip()) < 5:
        raise InvalidInputError("Judul pengaduan terlalu singkat (minimal 5 karakter).")
    if not deskripsi or len(str(deskripsi).strip()) < 10:
        raise InvalidInputError("Deskripsi pengaduan wajib diisi dengan jelas (minimal 10 karakter).")


def validate_status_transition(current_status: str, new_status: str) -> None:
    if new_status not in VALID_STATUSES:
        raise PengaduanError(f"Status '{new_status}' tidak valid.")
    
    allowed_next_statuses = VALID_TRANSITIONS.get(current_status, set())
    if new_status not in allowed_next_statuses:
        raise InvalidStatusTransitionError(
            f"Tidak dapat mengubah status pengaduan dari {current_status} menjadi {new_status}."
        )


def validate_resolution_note(new_status: str, notes: str | None) -> None:
    """Admin wajib memberikan catatan saat status berubah ke RESOLVED atau CLOSED."""
    if new_status in {STATUS_RESOLVED, STATUS_CLOSED}:
        if not notes or not str(notes).strip():
            raise NoteRequiredError(f"Catatan tindak lanjut wajib diisi saat mengubah status menjadi {new_status}.")
```

---

## File: `repositories.py`

```python
# features/pengaduan_warga/repositories.py

from django.db import transaction
from django.db.models import QuerySet

from features.pengaduan_warga.domain import STATUS_OPEN
from features.pengaduan_warga.models import LayananPengaduan, LayananPengaduanHistory


class PengaduanRepository:
    def get_by_id(self, pengaduan_id) -> LayananPengaduan | None:
        return LayananPengaduan.objects.select_related("pelapor").filter(id=pengaduan_id).first()

    def list_by_pelapor(self, pelapor_id) -> QuerySet[LayananPengaduan]:
        return LayananPengaduan.objects.filter(pelapor_id=pelapor_id)

    def list_all(self) -> QuerySet[LayananPengaduan]:
        return LayananPengaduan.objects.select_related("pelapor").all()

    @transaction.atomic
    def create_pengaduan(self, pelapor_id, kategori: str, judul: str, deskripsi: str, foto_bukti=None) -> LayananPengaduan:
        pengaduan = LayananPengaduan.objects.create(
            pelapor_id=pelapor_id,
            kategori=kategori,
            judul=judul,
            deskripsi=deskripsi,
            foto_bukti=foto_bukti,
            status=STATUS_OPEN
        )
        
        LayananPengaduanHistory.objects.create(
            pengaduan=pengaduan,
            status_from=None,
            status_to=STATUS_OPEN,
            changed_by_id=pelapor_id,
            notes="Pengaduan baru dibuat."
        )
        return pengaduan

    @transaction.atomic
    def update_status(self, pengaduan: LayananPengaduan, new_status: str, actor_id, notes: str | None = None) -> LayananPengaduan:
        old_status = pengaduan.status
        pengaduan.status = new_status
        pengaduan.save(update_fields=["status", "updated_at"])

        LayananPengaduanHistory.objects.create(
            pengaduan=pengaduan,
            status_from=old_status,
            status_to=new_status,
            changed_by_id=actor_id,
            notes=notes
        )
        return pengaduan
```

---

## File: `services.py`

```python
# features/pengaduan_warga/services.py

from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from features.pengaduan_warga.domain import (
    PengaduanError,
    validate_pengaduan_input,
    validate_resolution_note,
    validate_status_transition,
)
from features.pengaduan_warga.models import LayananPengaduan
from features.pengaduan_warga.permissions import (
    can_submit_pengaduan,
    can_update_pengaduan_status,
    can_view_pengaduan_detail,
)
from features.pengaduan_warga.repositories import PengaduanRepository
from toolbox.logging import audit_event, get_logger
from toolbox.security.permissions import can_view_all_pengaduan
from toolbox.security.upload_validators import validate_image_upload


class PermissionDeniedError(Exception):
    pass

class PengaduanNotFoundError(Exception):
    pass

class FileUploadError(Exception):
    pass


class PengaduanService:
    def __init__(self, repository: PengaduanRepository | None = None):
        self.repository = repository or PengaduanRepository()
        self.logger = get_logger("features.pengaduan_warga.services")

    def buat_pengaduan(self, actor, kategori: str, judul: str, deskripsi: str, foto_bukti=None) -> LayananPengaduan:
        if not can_submit_pengaduan(actor):
            raise PermissionDeniedError("Hanya warga yang dapat membuat pengaduan.")

        validate_pengaduan_input(kategori, judul, deskripsi)

        if foto_bukti:
            try:
                validate_image_upload(foto_bukti)
            except ValidationError as e:
                raise FileUploadError(str(e.message))

        pengaduan = self.repository.create_pengaduan(
            pelapor_id=actor.id,
            kategori=kategori.strip(),
            judul=judul.strip(),
            deskripsi=deskripsi.strip(),
            foto_bukti=foto_bukti
        )

        audit_event(
            action="PENGADUAN_CREATED",
            actor_id=actor.id,
            actor_role=actor.role,
            target="layanan_pengaduan",
            target_id=pengaduan.id,
            metadata={"kategori": kategori}
        )

        return pengaduan

    def get_pengaduan_detail(self, actor, pengaduan_id) -> LayananPengaduan:
        pengaduan = self.repository.get_by_id(pengaduan_id)
        if not pengaduan:
            raise PengaduanNotFoundError("Data pengaduan tidak ditemukan.")

        if not can_view_pengaduan_detail(actor, pengaduan):
            raise PermissionDeniedError("Anda tidak memiliki akses ke pengaduan ini.")

        return pengaduan

    def list_pengaduan(self, actor) -> QuerySet[LayananPengaduan]:
        if can_view_all_pengaduan(actor):
            return self.repository.list_all()
        return self.repository.list_by_pelapor(actor.id)

    def proses_pengaduan(self, actor, pengaduan_id, new_status: str, notes: str | None = None) -> LayananPengaduan:
        if not can_update_pengaduan_status(actor):
            raise PermissionDeniedError("Anda tidak memiliki izin untuk memproses pengaduan.")

        pengaduan = self.repository.get_by_id(pengaduan_id)
        if not pengaduan:
            raise PengaduanNotFoundError("Data pengaduan tidak ditemukan.")

        validate_status_transition(pengaduan.status, new_status)
        validate_resolution_note(new_status, notes)

        updated_pengaduan = self.repository.update_status(
            pengaduan=pengaduan,
            new_status=new_status,
            actor_id=actor.id,
            notes=notes
        )

        audit_event(
            action="PENGADUAN_STATUS_UPDATED",
            actor_id=actor.id,
            actor_role=actor.role,
            target="layanan_pengaduan",
            target_id=pengaduan.id,
            metadata={"old_status": pengaduan.status, "new_status": new_status}
        )

        return updated_pengaduan
```

---

## File: `permissions.py`

```python
# features/pengaduan_warga/permissions.py

from toolbox.security.auth import is_active_user, is_warga
from toolbox.security.permissions import can_handle_pengaduan, can_view_all_pengaduan


def can_submit_pengaduan(actor) -> bool:
    return is_active_user(actor) and is_warga(actor)


def can_view_pengaduan_detail(actor, pengaduan) -> bool:
    if not is_active_user(actor):
        return False
    if can_view_all_pengaduan(actor):
        return True
    return str(pengaduan.pelapor_id) == str(actor.id)


def can_update_pengaduan_status(actor) -> bool:
    return can_handle_pengaduan(actor)
```

---

## File: `schemas.py`

```python
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
```

---

## File: `api.py`

```python
# features/pengaduan_warga/api.py

from typing import List
from ninja import Router, Form, File
from ninja.files import UploadedFile

from .schemas import (
    BuatPengaduanIn, 
    PengaduanListOut, 
    PengaduanDetailOut, 
    ProsesPengaduanIn
)
from .services import PengaduanService
from toolbox.api.auth import AuthActiveUser, AuthAdminOnly

router = Router(tags=["Pengaduan Warga"])

# Dependency Inversion Principle: Kita inject class service
pengaduan_service = PengaduanService()


@router.post("/buat", auth=AuthActiveUser, response={201: PengaduanListOut})
def buat_pengaduan_api(
    request, 
    payload: Form[BuatPengaduanIn], 
    foto_bukti: File[UploadedFile] = None
):
    """
    Endpoint untuk warga membuat pengaduan.
    Menerima Multipart/Form-Data karena ada upload foto opsional.
    """
    pengaduan = pengaduan_service.buat_pengaduan(
        actor=request.user,
        kategori=payload.kategori,
        judul=payload.judul,
        deskripsi=payload.deskripsi,
        foto_bukti=foto_bukti
    )
    return 201, pengaduan


@router.get("/", auth=AuthActiveUser, response=List[PengaduanListOut])
def list_pengaduan_api(request):
    """Menampilkan daftar pengaduan (Warga lihat miliknya, Admin lihat semua)."""
    return pengaduan_service.list_pengaduan(request.user)


@router.get("/{pengaduan_id}", auth=AuthActiveUser, response=PengaduanDetailOut)
def detail_pengaduan_api(request, pengaduan_id: int):
    """Menampilkan detail pengaduan beserta riwayat tindak lanjutnya."""
    return pengaduan_service.get_pengaduan_detail(request.user, pengaduan_id)


@router.post("/{pengaduan_id}/proses", auth=AuthAdminOnly, response=PengaduanListOut)
def proses_pengaduan_api(request, pengaduan_id: int, payload: ProsesPengaduanIn):
    """
    Endpoint untuk Admin memproses/mengubah status pengaduan.
    Hanya menerima JSON.
    """
    updated_pengaduan = pengaduan_service.proses_pengaduan(
        actor=request.user,
        pengaduan_id=pengaduan_id,
        new_status=payload.status,
        notes=payload.notes
    )
    return updated_pengaduan
```

---
