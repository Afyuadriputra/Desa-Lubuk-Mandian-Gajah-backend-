# Feature Context: pengaduan_warga

Generated at: 2026-04-17T14:51:50
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
- `views.py`
- `urls.py`

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

## File: `views.py`

```python
# features/pengaduan_warga/views.py

import json

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from features.pengaduan_warga.domain import PengaduanError
from features.pengaduan_warga.services import (
    FileUploadError,
    PengaduanNotFoundError,
    PengaduanService,
    PermissionDeniedError,
)
from toolbox.security.auth import is_active_user

pengaduan_service = PengaduanService()


def _parse_json_body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


@require_POST
def buat_pengaduan_view(request):
    """Menerima Multipart/Form-Data karena ada upload gambar opsional."""
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    kategori = request.POST.get("kategori", "")
    judul = request.POST.get("judul", "")
    deskripsi = request.POST.get("deskripsi", "")
    foto_bukti = request.FILES.get("foto_bukti")

    try:
        pengaduan = pengaduan_service.buat_pengaduan(
            actor=actor,
            kategori=kategori,
            judul=judul,
            deskripsi=deskripsi,
            foto_bukti=foto_bukti
        )
    except PengaduanError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except FileUploadError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)

    return JsonResponse(
        {
            "detail": "Pengaduan berhasil dibuat.",
            "data": {
                "id": pengaduan.id,
                "status": pengaduan.status,
                "kategori": pengaduan.kategori,
                "created_at": pengaduan.created_at.isoformat(),
            }
        },
        status=201
    )


@require_GET
def list_pengaduan_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    qs = pengaduan_service.list_pengaduan(actor)
    data = [
        {
            "id": p.id,
            "judul": p.judul,
            "kategori": p.kategori,
            "status": p.status,
            "pelapor": p.pelapor.nama_lengkap,
            "created_at": p.created_at.isoformat(),
        } for p in qs
    ]

    return JsonResponse({"data": data}, status=200)


@require_GET
def detail_pengaduan_view(request, pengaduan_id):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    try:
        pengaduan = pengaduan_service.get_pengaduan_detail(actor, pengaduan_id)
    except PengaduanNotFoundError as exc:
        return JsonResponse({"detail": str(exc)}, status=404)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)

    histori = [
        {
            "status_to": h.status_to,
            "notes": h.notes,
            "created_at": h.created_at.isoformat(),
            "changed_by": h.changed_by.nama_lengkap if h.changed_by else "System"
        }
        for h in pengaduan.histori_tindak_lanjut.all()
    ]

    return JsonResponse(
        {
            "data": {
                "id": pengaduan.id,
                "kategori": pengaduan.kategori,
                "judul": pengaduan.judul,
                "deskripsi": pengaduan.deskripsi,
                "status": pengaduan.status,
                "foto_bukti_url": pengaduan.foto_bukti.url if pengaduan.foto_bukti else None,
                "pelapor": {
                    "nama_lengkap": pengaduan.pelapor.nama_lengkap,
                },
                "histori": histori,
                "created_at": pengaduan.created_at.isoformat(),
                "updated_at": pengaduan.updated_at.isoformat(),
            }
        },
        status=200
    )


@require_POST
def proses_pengaduan_view(request, pengaduan_id):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Payload JSON tidak valid."}, status=400)

    try:
        pengaduan = pengaduan_service.proses_pengaduan(
            actor=actor,
            pengaduan_id=pengaduan_id,
            new_status=payload.get("status", ""),
            notes=payload.get("notes")
        )
    except PengaduanError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)
    except PengaduanNotFoundError as exc:
        return JsonResponse({"detail": str(exc)}, status=404)

    return JsonResponse(
        {
            "detail": "Status pengaduan berhasil diperbarui.",
            "data": {
                "id": pengaduan.id,
                "status": pengaduan.status,
            }
        },
        status=200
    )
```

---

## File: `urls.py`

```python
# features/pengaduan_warga/urls.py

from django.urls import path

from features.pengaduan_warga.views import (
    buat_pengaduan_view,
    detail_pengaduan_view,
    list_pengaduan_view,
    proses_pengaduan_view,
)

urlpatterns = [
    path("pengaduan/", list_pengaduan_view, name="pengaduan-list"),
    path("pengaduan/buat/", buat_pengaduan_view, name="pengaduan-buat"),
    path("pengaduan/<int:pengaduan_id>/", detail_pengaduan_view, name="pengaduan-detail"),
    path("pengaduan/<int:pengaduan_id>/proses/", proses_pengaduan_view, name="pengaduan-proses"),
]
```

---
