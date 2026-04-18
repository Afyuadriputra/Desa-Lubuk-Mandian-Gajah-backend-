# Feature Context: profil_wilayah

Generated at: 2026-04-17T14:51:50
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
- `views.py`
- `urls.py`

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

    def perbarui_profil(self, actor, visi: str, misi: str, sejarah: str):
        if not can_manage_data_wilayah(actor):
            raise ProfilWilayahAccessError("Akses ditolak.")
        validate_profil_desa(visi, misi, sejarah)
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

## File: `views.py`

```python
# features/profil_wilayah/views.py

import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from features.profil_wilayah.services import DusunService, PerangkatService, ProfilDesaService
from toolbox.security.auth import is_active_user

dusun_service = DusunService()
perangkat_service = PerangkatService()
profil_service = ProfilDesaService()

@require_GET
def profil_publik_view(request):
    """Menampilkan Visi, Misi, Sejarah dan Perangkat Desa yang aktif."""
    profil = profil_service.get_profil()
    perangkat = perangkat_service.get_perangkat_publik()
    
    return JsonResponse({
        "profil": {"visi": profil.visi, "misi": profil.misi, "sejarah": profil.sejarah},
        "perangkat": [{"jabatan": p.jabatan, "nama": p.user.nama_lengkap, "foto_url": p.foto.url if p.foto else None} for p in perangkat]
    }, status=200)

@require_POST
def tambah_dusun_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor): return JsonResponse({"detail": "Unauthorized"}, status=401)
    
    data = json.loads(request.body.decode("utf-8") or "{}")
    try:
        dusun = dusun_service.tambah_dusun(actor, data.get("nama_dusun"), data.get("kepala_dusun"))
        return JsonResponse({"detail": "Dusun berhasil ditambahkan", "id": dusun.id}, status=201)
    except Exception as e:
        return JsonResponse({"detail": str(e)}, status=400)

@require_POST
def tambah_perangkat_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor): return JsonResponse({"detail": "Unauthorized"}, status=401)
    
    try:
        perangkat = perangkat_service.tambah_perangkat(
            actor=actor,
            user_id=request.POST.get("user_id"),
            jabatan=request.POST.get("jabatan"),
            is_published=request.POST.get("is_published", "false").lower() == "true",
            foto=request.FILES.get("foto")
        )
        return JsonResponse({"detail": "Perangkat berhasil ditambahkan", "id": perangkat.id}, status=201)
    except Exception as e:
        return JsonResponse({"detail": str(e)}, status=400)
```

---

## File: `urls.py`

```python
# features/profil_wilayah/urls.py

from django.urls import path
from features.profil_wilayah.views import profil_publik_view, tambah_dusun_view, tambah_perangkat_view

urlpatterns = [
    path("profil/publik/", profil_publik_view, name="profil-publik"),
    path("profil/admin/dusun/", tambah_dusun_view, name="admin-dusun-tambah"),
    path("profil/admin/perangkat/", tambah_perangkat_view, name="admin-perangkat-tambah"),
]
```

---
