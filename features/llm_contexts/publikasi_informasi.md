# Feature Context: publikasi_informasi

Generated at: 2026-04-18T23:18:05
Feature path: `D:\Kuliah\joki\radit\desa\backend\features\publikasi_informasi`

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


class PublikasiInformasiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'features.publikasi_informasi'
```

---

## File: `models.py`

```python
from django.db import models

# Create your models here.
# features/publikasi_informasi/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify

from features.publikasi_informasi.domain import VALID_STATUS, VALID_JENIS


class Publikasi(models.Model):
    STATUS_CHOICES = [(s, s) for s in VALID_STATUS]
    JENIS_CHOICES = [(j, j) for j in VALID_JENIS]

    id = models.BigAutoField(primary_key=True)
    judul = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    konten_html = models.TextField()
    jenis = models.CharField(max_length=20, choices=JENIS_CHOICES, default="BERITA")
    
    penulis = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    published_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "publikasi_informasi"
        ordering = ["-published_at", "-created_at"]

    def save(self, *args, **kwargs):
        # Auto-generate unique slug dari judul jika belum ada
        if not self.slug:
            base_slug = slugify(self.judul)
            unique_slug = base_slug
            counter = 1
            while Publikasi.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.jenis}] {self.judul} ({self.status})"
```

---

## File: `domain.py`

```python
# features/publikasi_informasi/domain.py

STATUS_DRAFT = "DRAFT"
STATUS_PUBLISHED = "PUBLISHED"

JENIS_BERITA = "BERITA"
JENIS_PENGUMUMAN = "PENGUMUMAN"

VALID_STATUS = {STATUS_DRAFT, STATUS_PUBLISHED}
VALID_JENIS = {JENIS_BERITA, JENIS_PENGUMUMAN}


class PublikasiError(Exception):
    """Base exception untuk domain publikasi."""


def validate_publikasi_input(judul: str, konten_html: str, jenis: str, status: str) -> None:
    if not judul or len(str(judul).strip()) < 5:
        raise PublikasiError("Judul terlalu pendek (minimal 5 karakter).")
    
    if not konten_html or len(str(konten_html).strip()) < 10:
        raise PublikasiError("Konten tidak boleh kosong atau terlalu pendek.")
        
    if jenis not in VALID_JENIS:
        raise PublikasiError(f"Jenis publikasi '{jenis}' tidak dikenali.")
        
    if status not in VALID_STATUS:
        raise PublikasiError(f"Status '{status}' tidak valid.")
```

---

## File: `repositories.py`

```python
# features/publikasi_informasi/repositories.py

from django.db.models import QuerySet
from features.publikasi_informasi.models import Publikasi
from features.publikasi_informasi.domain import STATUS_PUBLISHED

class PublikasiRepository:
    def get_by_slug(self, slug: str) -> Publikasi | None:
        return Publikasi.objects.select_related("penulis").filter(slug=slug).first()

    def list_published(self, jenis: str | None = None) -> QuerySet[Publikasi]:
        qs = Publikasi.objects.select_related("penulis").filter(status=STATUS_PUBLISHED)
        if jenis:
            qs = qs.filter(jenis=jenis)
        return qs

    def list_all_admin(self) -> QuerySet[Publikasi]:
        return Publikasi.objects.select_related("penulis").all()

    def create(self, data: dict) -> Publikasi:
        return Publikasi.objects.create(**data)

    def update_status(self, publikasi: Publikasi, status: str, published_at) -> Publikasi:
        publikasi.status = status
        publikasi.published_at = published_at
        publikasi.save(update_fields=["status", "published_at", "updated_at"])
        return publikasi
```

---

## File: `services.py`

```python
# features/publikasi_informasi/services.py

from django.utils import timezone
from features.publikasi_informasi.domain import (
    PublikasiError, validate_publikasi_input, STATUS_PUBLISHED
)
from features.publikasi_informasi.permissions import can_create_or_edit_publikasi
from features.publikasi_informasi.repositories import PublikasiRepository
from toolbox.logging import audit_event
# Import sanitize_rich_text_content DIHAPUS

class PublikasiAccessError(Exception):
    pass

class PublikasiService:
    def __init__(self, repo: PublikasiRepository = None):
        self.repo = repo or PublikasiRepository()

    def buat_publikasi(self, actor, judul: str, konten_html: str, jenis: str, status: str):
        if not can_create_or_edit_publikasi(actor):
            raise PublikasiAccessError("Anda tidak memiliki izin mengelola publikasi.")

        validate_publikasi_input(judul, konten_html, jenis, status)

        # KISS: Tidak perlu lagi memanggil sanitize_rich_text_content(konten_html) manual!
        # Variabel 'konten_html' di sini sudah dijamin aman oleh Pydantic.

        published_at = timezone.now() if status == STATUS_PUBLISHED else None

        publikasi = self.repo.create({
            "judul": judul, # Sudah otomatis di .strip() oleh SafePlainTextString
            "konten_html": konten_html,
            "jenis": jenis,
            "status": status,
            "penulis_id": actor.id,
            "published_at": published_at
        })

        audit_event("PUBLIKASI_CREATED", actor_id=actor.id, target_id=publikasi.id, metadata={"jenis": jenis})
        return publikasi

    def ubah_status(self, actor, slug: str, new_status: str):
        if not can_create_or_edit_publikasi(actor):
            raise PublikasiAccessError("Akses ditolak.")
            
        publikasi = self.repo.get_by_slug(slug)
        if not publikasi:
            raise PublikasiError("Publikasi tidak ditemukan.")

        published_at = timezone.now() if new_status == STATUS_PUBLISHED else None
        updated = self.repo.update_status(publikasi, new_status, published_at)
        
        audit_event("PUBLIKASI_STATUS_UPDATED", actor_id=actor.id, target_id=updated.id, metadata={"new_status": new_status})
        return updated

    def get_publikasi_publik(self, jenis=None):
        """Hanya mengembalikan data yang berstatus PUBLISHED."""
        return self.repo.list_published(jenis=jenis)

    def get_detail_publik(self, slug: str):
        publikasi = self.repo.get_by_slug(slug)
        if not publikasi or publikasi.status != STATUS_PUBLISHED:
            raise PublikasiError("Konten tidak ditemukan atau belum dipublikasikan.")
        return publikasi
```

---

## File: `permissions.py`

```python
# features/publikasi_informasi/permissions.py

from toolbox.security.auth import is_active_user
from toolbox.security.permissions import can_manage_publikasi


def can_create_or_edit_publikasi(actor) -> bool:
    """Hanya Admin Desa dan Super Admin yang bisa menambah/mengedit publikasi."""
    return can_manage_publikasi(actor)


def can_view_publikasi_publik(actor) -> bool:
    """Semua warga (bahkan mungkin publik tanpa login) bisa melihat publikasi."""
    return True
```

---

## File: `schemas.py`

```python
# features/publikasi_informasi/schemas.py

from datetime import datetime
from typing import Optional
from ninja import Schema, Field
from toolbox.security.sanitizers import SafeHTMLString, SafePlainTextString

# --- INPUT SCHEMAS ---

class BuatPublikasiIn(Schema):
    """
    DRY: SafePlainTextString dan SafeHTMLString otomatis membersihkan 
    input dari potensi XSS Attack saat request masuk.
    """
    judul: SafePlainTextString
    konten_html: SafeHTMLString
    jenis: str = "BERITA"
    status: str = "DRAFT"

class UbahStatusIn(Schema):
    status: str


# --- OUTPUT SCHEMAS ---

class PublikasiListOut(Schema):
    """
    YAGNI: Hanya mengirim data meta untuk card/daftar berita.
    Tidak perlu mengirim 'konten_html' di sini untuk menghemat bandwidth.
    """
    judul: str
    slug: str
    jenis: str
    penulis_nama: str = Field("Admin", alias="penulis.nama_lengkap")
    published_at: Optional[datetime] = None

class PublikasiDetailOut(Schema):
    """Schema lengkap untuk halaman baca artikel."""
    judul: str
    slug: str
    konten_html: str
    jenis: str
    status: str
    penulis_nama: str = Field("Admin", alias="penulis.nama_lengkap")
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
```

---

## File: `api.py`

```python
# features/publikasi_informasi/api.py
from typing import List, Optional
from ninja import Router

from .schemas import BuatPublikasiIn, PublikasiListOut, PublikasiDetailOut, UbahStatusIn
from .services import PublikasiService
from toolbox.api.auth import AuthAdminOnly

router = Router(tags=["Publikasi Informasi (CMS)"])
publikasi_service = PublikasiService()

@router.get("/publik", auth=None, response=list[PublikasiListOut])
def list_publikasi_publik_api(request, jenis: Optional[str] = None):
    return publikasi_service.get_publikasi_publik(jenis=jenis)

@router.get("/publik/{slug}", auth=None, response=PublikasiDetailOut)
def detail_publikasi_api(request, slug: str):
    return publikasi_service.get_detail_publik(slug)

@router.post("/admin/buat", auth=AuthAdminOnly, response={201: PublikasiDetailOut})
def buat_publikasi_admin_api(request, payload: BuatPublikasiIn):
    publikasi = publikasi_service.buat_publikasi(
        actor=request.user,
        judul=payload.judul,
        konten_html=payload.konten_html,
        jenis=payload.jenis,
        status=payload.status
    )
    return 201, publikasi

@router.put("/admin/{slug}/status", auth=AuthAdminOnly, response=PublikasiDetailOut)
def ubah_status_publikasi_api(request, slug: str, payload: UbahStatusIn):
    updated_publikasi = publikasi_service.ubah_status(
        actor=request.user,
        slug=slug,
        new_status=payload.status
    )
    return updated_publikasi
```

---
