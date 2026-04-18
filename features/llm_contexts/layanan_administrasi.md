# Feature Context: layanan_administrasi

Generated at: 2026-04-18T23:18:05
Feature path: `D:\Kuliah\joki\radit\desa\backend\features\layanan_administrasi`

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


class LayananAdministrasiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "features.layanan_administrasi"
```

---

## File: `models.py`

```python
# features/layanan_administrasi/models.py

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

from features.layanan_administrasi.domain import (
    STATUS_PENDING,
    VALID_JENIS_SURAT,
    VALID_STATUSES,
)
from toolbox.storage.paths import surat_pdf_upload_path


class LayananSurat(models.Model):
    JENIS_CHOICES = [(j, j) for j in VALID_JENIS_SURAT]
    STATUS_CHOICES = [(s, s) for s in VALID_STATUSES]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pemohon = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="surat_diajukan"
    )
    jenis_surat = models.CharField(max_length=50, choices=JENIS_CHOICES)
    keperluan = models.TextField()
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default=STATUS_PENDING
    )
    nomor_surat = models.CharField(max_length=100, blank=True, null=True)
    pdf_file = models.FileField(upload_to=surat_pdf_upload_path, blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "layanan_surat"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.jenis_surat} - {self.pemohon.nama_lengkap} ({self.status})"


class LayananSuratStatusHistory(models.Model):
    surat = models.ForeignKey(
        LayananSurat, 
        on_delete=models.CASCADE, 
        related_name="histori_status"
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
        db_table = "layanan_surat_status_history"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.surat.id} : {self.status_from} -> {self.status_to}"
```

---

## File: `domain.py`

```python
# features/layanan_administrasi/domain.py

JENIS_SKU = "SKU"
JENIS_SKTM = "SKTM"
JENIS_DOMISILI = "DOMISILI"

VALID_JENIS_SURAT = {JENIS_SKU, JENIS_SKTM, JENIS_DOMISILI}

STATUS_PENDING = "PENDING"
STATUS_VERIFIED = "VERIFIED"
STATUS_PROCESSED = "PROCESSED"
STATUS_DONE = "DONE"
STATUS_REJECTED = "REJECTED"

VALID_STATUSES = {
    STATUS_PENDING,
    STATUS_VERIFIED,
    STATUS_PROCESSED,
    STATUS_DONE,
    STATUS_REJECTED,
}

# State Machine: Menentukan status apa saja yang valid untuk dituju dari status saat ini
VALID_TRANSITIONS = {
    STATUS_PENDING: {STATUS_VERIFIED, STATUS_REJECTED},
    STATUS_VERIFIED: {STATUS_PROCESSED, STATUS_REJECTED},
    STATUS_PROCESSED: {STATUS_DONE, STATUS_REJECTED},
    STATUS_DONE: set(),      # Terminal state
    STATUS_REJECTED: set(),  # Terminal state
}


class LayananSuratError(Exception):
    """Base exception untuk domain layanan surat."""


class InvalidJenisSuratError(LayananSuratError):
    """Jenis surat tidak valid."""


class InvalidStatusTransitionError(LayananSuratError):
    """Transisi status tidak diizinkan."""


class InvalidKeperluanError(LayananSuratError):
    """Keperluan surat tidak valid atau kosong."""


class RejectionReasonRequiredError(LayananSuratError):
    """Alasan penolakan wajib diisi jika status REJECTED."""


def validate_jenis_surat(jenis: str) -> None:
    if jenis not in VALID_JENIS_SURAT:
        raise InvalidJenisSuratError(f"Jenis surat '{jenis}' tidak valid.")


def validate_keperluan(keperluan: str | None) -> None:
    if not keperluan or not str(keperluan).strip():
        raise InvalidKeperluanError("Keperluan pengajuan surat wajib diisi.")
    if len(str(keperluan)) < 10:
        raise InvalidKeperluanError("Deskripsi keperluan terlalu singkat (minimal 10 karakter).")


def validate_status_transition(current_status: str, new_status: str) -> None:
    if new_status not in VALID_STATUSES:
        raise LayananSuratError(f"Status '{new_status}' tidak dikenali.")
    
    allowed_next_statuses = VALID_TRANSITIONS.get(current_status, set())
    if new_status not in allowed_next_statuses:
        raise InvalidStatusTransitionError(
            f"Tidak dapat mengubah status dari {current_status} menjadi {new_status}."
        )


def validate_rejection(status: str, rejection_reason: str | None) -> None:
    if status == STATUS_REJECTED:
        if not rejection_reason or not str(rejection_reason).strip():
            raise RejectionReasonRequiredError("Alasan penolakan wajib diisi.")
```

---

## File: `repositories.py`

```python
# features/layanan_administrasi/repositories.py

from django.db import transaction
from django.db.models import QuerySet

from features.layanan_administrasi.models import LayananSurat, LayananSuratStatusHistory


class SuratRepository:
    def get_by_id(self, surat_id) -> LayananSurat | None:
        return LayananSurat.objects.select_related("pemohon").filter(id=surat_id).first()

    def list_by_pemohon(self, pemohon_id) -> QuerySet[LayananSurat]:
        return LayananSurat.objects.filter(pemohon_id=pemohon_id)

    def list_all(self) -> QuerySet[LayananSurat]:
        return LayananSurat.objects.select_related("pemohon").all()

    @transaction.atomic
    def create_surat(self, pemohon_id, jenis_surat: str, keperluan: str) -> LayananSurat:
        surat = LayananSurat.objects.create(
            pemohon_id=pemohon_id,
            jenis_surat=jenis_surat,
            keperluan=keperluan,
            status="PENDING"
        )
        
        # Rekam histori awal
        LayananSuratStatusHistory.objects.create(
            surat=surat,
            status_from=None,
            status_to="PENDING",
            changed_by_id=pemohon_id,
            notes="Pengajuan surat baru."
        )
        return surat

    @transaction.atomic
    def update_status(
        self, 
        surat: LayananSurat, 
        new_status: str, 
        actor_id, 
        notes: str | None = None,
        nomor_surat: str | None = None,
        rejection_reason: str | None = None
    ) -> LayananSurat:
        old_status = surat.status
        surat.status = new_status
        
        if nomor_surat:
            surat.nomor_surat = nomor_surat
        if rejection_reason and new_status == "REJECTED":
            surat.rejection_reason = rejection_reason
            
        surat.save()

        LayananSuratStatusHistory.objects.create(
            surat=surat,
            status_from=old_status,
            status_to=new_status,
            changed_by_id=actor_id,
            notes=notes
        )
        return surat
```

---

## File: `services.py`

```python
# features/layanan_administrasi/services.py

from django.core.files.base import ContentFile
from django.db.models import QuerySet
from django.utils import timezone

from features.layanan_administrasi.domain import (
    STATUS_DONE,
    STATUS_REJECTED,
    validate_jenis_surat,
    validate_keperluan,
    validate_rejection,
    validate_status_transition,
)
from features.layanan_administrasi.models import LayananSurat
from features.layanan_administrasi.permissions import (
    can_submit_surat,
    can_update_surat_status,
    can_view_surat_detail,
)
from features.layanan_administrasi.repositories import SuratRepository
from toolbox.logging import audit_event, get_logger
from toolbox.security.permissions import can_view_all_surat

# Import dari toolbox PDF generator yang sudah Anda buat
from toolbox.pdf_generator import (
    generate_nomor_surat,
    generate_pdf_from_html,
    render_surat_html,
)


class PermissionDeniedError(Exception):
    pass


class LayananSuratNotFoundError(Exception):
    pass


class SuratService:
    def __init__(self, repository: SuratRepository | None = None):
        self.repository = repository or SuratRepository()
        self.logger = get_logger("features.layanan_administrasi.services")

    def ajukan_surat(self, actor, jenis_surat: str, keperluan: str) -> LayananSurat:
        if not can_submit_surat(actor):
            raise PermissionDeniedError("Hanya warga yang dapat mengajukan surat.")

        validate_jenis_surat(jenis_surat)
        validate_keperluan(keperluan)

        surat = self.repository.create_surat(
            pemohon_id=actor.id,
            jenis_surat=jenis_surat,
            keperluan=keperluan.strip()
        )

        audit_event(
            action="SURAT_SUBMITTED",
            actor_id=actor.id,
            actor_role=actor.role,
            target="layanan_surat",
            target_id=surat.id,
            metadata={"jenis_surat": jenis_surat}
        )

        self.logger.info("Pengajuan surat berhasil dibuat. ID={surat_id}", surat_id=surat.id)
        return surat

    def get_surat_detail(self, actor, surat_id) -> LayananSurat:
        surat = self.repository.get_by_id(surat_id)
        if not surat:
            raise LayananSuratNotFoundError("Data surat tidak ditemukan.")

        if not can_view_surat_detail(actor, surat):
            raise PermissionDeniedError("Anda tidak memiliki akses untuk melihat surat ini.")

        return surat

    def list_surat(self, actor) -> QuerySet[LayananSurat]:
        if can_view_all_surat(actor):
            return self.repository.list_all()
        return self.repository.list_by_pemohon(actor.id)

    def proses_surat(
        self, 
        actor, 
        surat_id, 
        new_status: str, 
        notes: str | None = None,
        nomor_surat: str | None = None,
        rejection_reason: str | None = None
    ) -> LayananSurat:
        if not can_update_surat_status(actor):
            raise PermissionDeniedError("Anda tidak memiliki izin memproses surat.")

        surat = self.repository.get_by_id(surat_id)
        if not surat:
            raise LayananSuratNotFoundError("Data surat tidak ditemukan.")

        # Validasi domain rules
        validate_status_transition(surat.status, new_status)
        validate_rejection(new_status, rejection_reason)

        # OTOMATISASI NOMOR SURAT
        final_nomor_surat = nomor_surat or surat.nomor_surat
        if new_status == STATUS_DONE and not final_nomor_surat:
            final_nomor_surat = generate_nomor_surat(surat.jenis_surat, str(surat.id))

        updated_surat = self.repository.update_status(
            surat=surat,
            new_status=new_status,
            actor_id=actor.id,
            notes=notes,
            nomor_surat=final_nomor_surat,
            rejection_reason=rejection_reason
        )

        # GENERATE PDF JIKA STATUS DONE
        if new_status == STATUS_DONE:
            try:
                self.logger.info("Memulai proses generate PDF untuk surat ID={id}", id=surat.id)
                
                context = {
                    "surat": updated_surat,
                    "pemohon": updated_surat.pemohon,
                    "tanggal_cetak": timezone.now(),
                    "nama_kepala_desa": "Bapak Kepala Desa", 
                }
                
                template_name = f"pdf_templates/surat_{updated_surat.jenis_surat.lower()}.html"
                html_string = render_surat_html(template_name, context)
                pdf_bytes = generate_pdf_from_html(html_string)
                
                pdf_filename = f"Surat_{updated_surat.jenis_surat}_{updated_surat.pemohon.nik}.pdf"
                updated_surat.pdf_file.save(pdf_filename, ContentFile(pdf_bytes), save=True)
                
                self.logger.info("Berhasil men-generate dan menyimpan PDF surat ID={id}", id=surat.id)

            except Exception as e:
                self.logger.error("Gagal men-generate PDF untuk surat ID={id}: {error}", id=surat.id, error=str(e))

        audit_event(
            action="SURAT_STATUS_UPDATED",
            actor_id=actor.id,
            actor_role=actor.role,
            target="layanan_surat",
            target_id=surat.id,
            metadata={"old_status": surat.status, "new_status": new_status, "pdf_generated": new_status == STATUS_DONE}
        )

        return updated_surat
```

---

## File: `permissions.py`

```python
# features/layanan_administrasi/permissions.py

from toolbox.security.auth import is_active_user, is_warga
from toolbox.security.permissions import can_process_surat, can_view_all_surat


def can_submit_surat(actor) -> bool:
    """Hanya warga aktif yang bisa mengajukan surat."""
    return is_active_user(actor) and is_warga(actor)


def can_view_surat_detail(actor, surat) -> bool:
    """Warga hanya bisa melihat suratnya sendiri, admin bisa melihat semua."""
    if not is_active_user(actor):
        return False
    if can_view_all_surat(actor):
        return True
    return str(surat.pemohon_id) == str(actor.id)


def can_update_surat_status(actor) -> bool:
    """Hanya internal admin (Admin Desa / Super Admin) yang bisa proses surat."""
    return can_process_surat(actor)
```

---

## File: `schemas.py`

```python
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
```

---

## File: `api.py`

```python
from ninja import Router
from .schemas import SuratIn, SuratOut, ProsesSuratIn
from .services import SuratService
from toolbox.api.auth import AuthActiveUser, AuthAdminOnly

router = Router(tags=["Layanan Administrasi"])
surat_service = SuratService()

@router.post("/surat/ajukan", auth=AuthActiveUser, response={201: SuratOut})
def ajukan_surat_api(request, payload: SuratIn):
    surat = surat_service.ajukan_surat(
        actor=request.user, 
        **payload.dict(exclude_unset=True)
    )
    return 201, surat

@router.get("/surat", auth=AuthActiveUser, response=list[SuratOut])
def list_surat_api(request):
    return surat_service.list_surat(request.user)

@router.post("/surat/{surat_id}/proses", auth=AuthAdminOnly, response=SuratOut)
def proses_surat_api(request, surat_id: str, payload: ProsesSuratIn):
    # Kita petakan secara manual agar nama parameter di API 
    # sinkron dengan nama parameter di Service Layer Anda.
    surat = surat_service.proses_surat(
        actor=request.user,
        surat_id=surat_id,
        new_status=payload.status,        # Map 'status' ke 'new_status'
        notes=payload.notes,               # Nama sudah sama
        nomor_surat=payload.nomor_surat,
        rejection_reason=payload.rejection_reason
    )
    return surat
```

---
