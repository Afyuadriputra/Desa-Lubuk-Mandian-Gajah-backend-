# Context Modul: potensi_ekonomi

## Tujuan Dokumen

Dokumen ini dibuat untuk membantu LLM memahami konteks modul secara akurat. Struktur disusun berdasarkan peran file dalam arsitektur Django modular berbasis feature.

## Metadata

- Nama modul: `potensi_ekonomi`
- Path modul: `D:/Kuliah/joki/radit/desa/backend/features/potensi_ekonomi`
- Digenerate pada: `2026-04-16 21:11:50`
- Project root: `D:/Kuliah/joki/radit/desa/backend`

## Panduan Membaca Modul untuk LLM

- `domain.py` berisi aturan bisnis murni dan validasi inti.
- `models.py` berisi struktur data yang tersimpan di database.
- `repositories.py` berisi akses data dan query persistence.
- `services.py` berisi use case dan orkestrasi alur bisnis.
- `permissions.py` berisi aturan otorisasi.
- `views.py` berisi antarmuka HTTP/API.
- `urls.py` menghubungkan route ke view.
- `tests/` menunjukkan perilaku yang diharapkan sistem.

Saat menganalisis bug atau membuat fitur baru, prioritaskan pembacaan file dalam urutan: `domain.py -> models.py -> repositories.py -> services.py -> permissions.py -> views.py -> urls.py -> tests/`.

## Struktur File

- `apps.py`
- `domain.py`
- `models.py`
- `permissions.py`
- `repositories.py`
- `services.py`
- `views.py`
- `urls.py`
- `admin.py`
- `__init__.py`
- `generate_llm_context.py`
- `tests/__init__.py`
- `migrations/__init__.py`

## Ringkasan Layer

- `apps.py`: Konfigurasi Django app untuk modul ini.
- `domain.py`: Aturan bisnis murni, validasi domain, konstanta, helper bisnis, dan logika yang tidak bergantung pada framework.
- `models.py`: Definisi model database Django, relasi antar entitas, field, dan perilaku model.
- `permissions.py`: Aturan otorisasi dan hak akses terhadap resource atau aksi di modul ini.
- `repositories.py`: Lapisan akses data untuk query, penyimpanan, update, atau abstraksi interaksi database.
- `services.py`: Use case / application service. Mengorkestrasi domain, repository, validasi, side effects, dan flow bisnis utama.
- `views.py`: Lapisan HTTP/API. Menerima request, memanggil service, menerapkan permission, dan mengembalikan response.
- `urls.py`: Pemetaan endpoint URL ke views.
- `admin.py`: Konfigurasi Django admin untuk model dalam modul ini.
- `__init__.py`: Penanda package Python. Biasanya minim logika.
- `generate_llm_context.py`: File tambahan pada modul.
- `tests/`: Skenario verifikasi perilaku sistem pada modul.
- `migrations/`: Riwayat perubahan skema database.

## Konteks Kode per File

### apps.py

**Peran:** Konfigurasi Django app untuk modul ini.

```python
from django.apps import AppConfig


class PotensiEkonomiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'features.potensi_ekonomi'
```

### domain.py

**Peran:** Aturan bisnis murni, validasi domain, konstanta, helper bisnis, dan logika yang tidak bergantung pada framework.

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

### models.py

**Peran:** Definisi model database Django, relasi antar entitas, field, dan perilaku model.

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

### permissions.py

**Peran:** Aturan otorisasi dan hak akses terhadap resource atau aksi di modul ini.

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

### repositories.py

**Peran:** Lapisan akses data untuk query, penyimpanan, update, atau abstraksi interaksi database.

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

### services.py

**Peran:** Use case / application service. Mengorkestrasi domain, repository, validasi, side effects, dan flow bisnis utama.

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
from toolbox.security.sanitizers import sanitize_rich_text_content
from toolbox.security.upload_validators import validate_image_upload


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

        validate_kategori(data.get("kategori"))
        validate_input_usaha(data.get("nama_usaha"), data.get("kontak_wa", ""))

        if foto:
            try:
                validate_image_upload(foto)
            except ValidationError as e:
                raise FileUploadError(str(e.message))

        # Sanitasi input HTML jika frontend menggunakan WYSIWYG editor
        clean_deskripsi = sanitize_rich_text_content(data.get("deskripsi", ""))
        clean_fasilitas = sanitize_rich_text_content(data.get("fasilitas", ""))

        create_data = {
            "nama_usaha": data.get("nama_usaha").strip(),
            "kategori": data.get("kategori"),
            "deskripsi": clean_deskripsi,
            "fasilitas": clean_fasilitas,
            "kontak_wa": data.get("kontak_wa", "").strip(),
            "harga_tiket": data.get("harga_tiket") or None,
            "is_published": str(data.get("is_published", "false")).lower() == "true",
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

### views.py

**Peran:** Lapisan HTTP/API. Menerima request, memanggil service, menerapkan permission, dan mengembalikan response.

```python
# features/potensi_ekonomi/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from features.potensi_ekonomi.domain import PotensiEkonomiError
from features.potensi_ekonomi.services import (
    FileUploadError,
    PermissionDeniedError,
    PotensiEkonomiService,
    UnitUsahaNotFoundError,
)
from toolbox.security.auth import is_active_user

ekonomi_service = PotensiEkonomiService()


@require_GET
def katalog_publik_view(request):
    """Endpoint untuk warga melihat katalog BUMDes/Wisata yang aktif."""
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    try:
        qs = ekonomi_service.get_katalog_publik(actor)
        data = [
            {
                "id": u.id,
                "nama_usaha": u.nama_usaha,
                "kategori": u.kategori,
                "deskripsi": u.deskripsi,
                "harga_tiket": u.harga_tiket,
                "foto_url": u.foto_utama.url if u.foto_utama else None,
            } for u in qs
        ]
        return JsonResponse({"data": data}, status=200)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)


@require_GET
def list_admin_view(request):
    """Endpoint untuk admin melihat semua data (termasuk draft)."""
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    try:
        qs = ekonomi_service.get_semua_unit_admin(actor)
        data = [
            {
                "id": u.id,
                "nama_usaha": u.nama_usaha,
                "kategori": u.kategori,
                "is_published": u.is_published,
                "created_at": u.created_at.isoformat(),
            } for u in qs
        ]
        return JsonResponse({"data": data}, status=200)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)


@require_POST
def buat_unit_usaha_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    # Menangani form-data karena ada upload gambar
    data_payload = {
        "nama_usaha": request.POST.get("nama_usaha"),
        "kategori": request.POST.get("kategori"),
        "deskripsi": request.POST.get("deskripsi"),
        "fasilitas": request.POST.get("fasilitas"),
        "kontak_wa": request.POST.get("kontak_wa"),
        "harga_tiket": request.POST.get("harga_tiket"),
        "is_published": request.POST.get("is_published", "false"),
    }
    foto = request.FILES.get("foto_utama")

    try:
        unit = ekonomi_service.buat_unit_usaha(actor, data_payload, foto)
    except PotensiEkonomiError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except FileUploadError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)

    return JsonResponse(
        {
            "detail": "Data BUMDes/Wisata berhasil ditambahkan.",
            "data": {
                "id": unit.id,
                "nama_usaha": unit.nama_usaha,
                "is_published": unit.is_published,
            }
        },
        status=201
    )


@require_GET
def detail_unit_view(request, unit_id):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    try:
        unit = ekonomi_service.get_detail_unit(actor, unit_id)
    except UnitUsahaNotFoundError as exc:
        return JsonResponse({"detail": str(exc)}, status=404)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)

    return JsonResponse(
        {
            "data": {
                "id": unit.id,
                "nama_usaha": unit.nama_usaha,
                "kategori": unit.kategori,
                "deskripsi": unit.deskripsi,
                "fasilitas": unit.fasilitas,
                "kontak_wa": unit.kontak_wa,
                "harga_tiket": unit.harga_tiket,
                "is_published": unit.is_published,
                "foto_url": unit.foto_utama.url if unit.foto_utama else None,
            }
        },
        status=200
    )
```

### urls.py

**Peran:** Pemetaan endpoint URL ke views.

```python
# features/potensi_ekonomi/urls.py

from django.urls import path

from features.potensi_ekonomi.views import (
    buat_unit_usaha_view,
    detail_unit_view,
    katalog_publik_view,
    list_admin_view,
)

urlpatterns = [
    path("ekonomi/katalog/", katalog_publik_view, name="ekonomi-katalog"),
    path("ekonomi/admin/list/", list_admin_view, name="ekonomi-admin-list"),
    path("ekonomi/admin/buat/", buat_unit_usaha_view, name="ekonomi-admin-buat"),
    path("ekonomi/<int:unit_id>/", detail_unit_view, name="ekonomi-detail"),
]
```

### admin.py

**Peran:** Konfigurasi Django admin untuk model dalam modul ini.

```python
from django.contrib import admin

# Register your models here.
```

### __init__.py

**Peran:** Penanda package Python. Biasanya minim logika.

```python
# File kosong
```

## File Tambahan

### generate_llm_context.py

**Peran:** File tambahan pada modul.

```python
from pathlib import Path
from datetime import datetime
import argparse

LAYER_DESCRIPTIONS = {
    "apps.py": "Konfigurasi Django app untuk modul ini.",
    "domain.py": "Aturan bisnis murni, validasi domain, konstanta, helper bisnis, dan logika yang tidak bergantung pada framework.",
    "models.py": "Definisi model database Django, relasi antar entitas, field, dan perilaku model.",
    "permissions.py": "Aturan otorisasi dan hak akses terhadap resource atau aksi di modul ini.",
    "repositories.py": "Lapisan akses data untuk query, penyimpanan, update, atau abstraksi interaksi database.",
    "services.py": "Use case / application service. Mengorkestrasi domain, repository, validasi, side effects, dan flow bisnis utama.",
    "views.py": "Lapisan HTTP/API. Menerima request, memanggil service, menerapkan permission, dan mengembalikan response.",
    "urls.py": "Pemetaan endpoint URL ke views.",
    "admin.py": "Konfigurasi Django admin untuk model dalam modul ini.",
    "__init__.py": "Penanda package Python. Biasanya minim logika.",
}

DEFAULT_ORDER = [
    "apps.py",
    "domain.py",
    "models.py",
    "permissions.py",
    "repositories.py",
    "services.py",
    "views.py",
    "urls.py",
    "admin.py",
    "__init__.py",
]

IGNORED_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".git", "venv", "env"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}
IGNORED_FILES = set()


def read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")
    except Exception as exc:
        return f"# Gagal membaca file: {exc}"


def clean_code_block(text: str) -> str:
    text = text.rstrip()
    if not text:
        return "# File kosong"
    return text


def collect_python_files(feature_path: Path) -> list[Path]:
    files = []
    for item in feature_path.rglob("*"):
        if item.is_dir():
            if item.name in IGNORED_DIRS:
                continue
            continue

        if item.suffix in IGNORED_SUFFIXES:
            continue

        if item.name in IGNORED_FILES:
            continue

        if "__pycache__" in item.parts:
            continue

        if item.is_file() and item.suffix == ".py":
            files.append(item)

    return sorted(files)


def ordered_main_files(feature_path: Path) -> list[Path]:
    result = []
    for name in DEFAULT_ORDER:
        file_path = feature_path / name
        if file_path.exists():
            result.append(file_path)
    return result


def find_extra_python_files(feature_path: Path) -> list[Path]:
    main_files = {p.resolve() for p in ordered_main_files(feature_path)}
    extra = []

    for p in collect_python_files(feature_path):
        if p.resolve() in main_files:
            continue
        if "migrations" in p.parts:
            continue
        if "tests" in p.parts:
            continue
        extra.append(p)

    return extra


def collect_test_files(feature_path: Path) -> list[Path]:
    tests_dir = feature_path / "tests"
    if not tests_dir.exists():
        return []
    result = []
    for p in tests_dir.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        result.append(p)
    return sorted(result)


def collect_migration_files(feature_path: Path) -> list[Path]:
    migrations_dir = feature_path / "migrations"
    if not migrations_dir.exists():
        return []
    result = []
    for p in migrations_dir.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        result.append(p)
    return sorted(result)


def relative_str(base: Path, target: Path) -> str:
    return str(target.relative_to(base)).replace("\\", "/")


def build_markdown(feature_path: Path, project_root: Path | None = None) -> str:
    feature_name = feature_path.name
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    main_files = ordered_main_files(feature_path)
    extra_files = find_extra_python_files(feature_path)
    test_files = collect_test_files(feature_path)
    migration_files = collect_migration_files(feature_path)

    lines = []
    lines.append(f"# Context Modul: {feature_name}")
    lines.append("")
    lines.append("## Tujuan Dokumen")
    lines.append("")
    lines.append(
        "Dokumen ini dibuat untuk membantu LLM memahami konteks modul secara akurat. "
        "Struktur disusun berdasarkan peran file dalam arsitektur Django modular berbasis feature."
    )
    lines.append("")
    lines.append("## Metadata")
    lines.append("")
    lines.append(f"- Nama modul: `{feature_name}`")
    lines.append(f"- Path modul: `{feature_path.as_posix()}`")
    lines.append(f"- Digenerate pada: `{generated_at}`")
    if project_root:
        lines.append(f"- Project root: `{project_root.as_posix()}`")
    lines.append("")

    lines.append("## Panduan Membaca Modul untuk LLM")
    lines.append("")
    lines.append("- `domain.py` berisi aturan bisnis murni dan validasi inti.")
    lines.append("- `models.py` berisi struktur data yang tersimpan di database.")
    lines.append("- `repositories.py` berisi akses data dan query persistence.")
    lines.append("- `services.py` berisi use case dan orkestrasi alur bisnis.")
    lines.append("- `permissions.py` berisi aturan otorisasi.")
    lines.append("- `views.py` berisi antarmuka HTTP/API.")
    lines.append("- `urls.py` menghubungkan route ke view.")
    lines.append("- `tests/` menunjukkan perilaku yang diharapkan sistem.")
    lines.append("")
    lines.append(
        "Saat menganalisis bug atau membuat fitur baru, prioritaskan pembacaan file dalam urutan: "
        "`domain.py -> models.py -> repositories.py -> services.py -> permissions.py -> views.py -> urls.py -> tests/`."
    )
    lines.append("")

    lines.append("## Struktur File")
    lines.append("")
    for p in main_files:
        lines.append(f"- `{p.name}`")
    if extra_files:
        for p in extra_files:
            lines.append(f"- `{relative_str(feature_path, p)}`")
    if test_files:
        for p in test_files:
            lines.append(f"- `{relative_str(feature_path, p)}`")
    if migration_files:
        for p in migration_files:
            lines.append(f"- `{relative_str(feature_path, p)}`")
    lines.append("")

    lines.append("## Ringkasan Layer")
    lines.append("")
    for p in main_files:
        desc = LAYER_DESCRIPTIONS.get(p.name, "File Python pada modul ini.")
        lines.append(f"- `{p.name}`: {desc}")
    if extra_files:
        for p in extra_files:
            lines.append(f"- `{relative_str(feature_path, p)}`: File tambahan pada modul.")
    if test_files:
        lines.append("- `tests/`: Skenario verifikasi perilaku sistem pada modul.")
    if migration_files:
        lines.append("- `migrations/`: Riwayat perubahan skema database.")
    lines.append("")

    lines.append("## Konteks Kode per File")
    lines.append("")

    for p in main_files:
        lines.append(f"### {p.name}")
        lines.append("")
        lines.append(f"**Peran:** {LAYER_DESCRIPTIONS.get(p.name, 'File Python pada modul ini.')}")
        lines.append("")
        lines.append("```python")
        lines.append(clean_code_block(read_text_file(p)))
        lines.append("```")
        lines.append("")

    if extra_files:
        lines.append("## File Tambahan")
        lines.append("")
        for p in extra_files:
            rel = relative_str(feature_path, p)
            lines.append(f"### {rel}")
            lines.append("")
            lines.append("**Peran:** File tambahan pada modul.")
            lines.append("")
            lines.append("```python")
            lines.append(clean_code_block(read_text_file(p)))
            lines.append("```")
            lines.append("")

    if test_files:
        lines.append("## Konteks Pengujian")
        lines.append("")
        lines.append(
            "Bagian ini penting untuk LLM karena test menunjukkan perilaku yang diharapkan, "
            "use case yang dijalankan, dan kontrak sistem yang harus dipertahankan."
        )
        lines.append("")
        for p in test_files:
            rel = relative_str(feature_path, p)
            lines.append(f"### {rel}")
            lines.append("")
            lines.append("**Peran:** File test untuk memverifikasi perilaku modul.")
            lines.append("")
            lines.append("```python")
            lines.append(clean_code_block(read_text_file(p)))
            lines.append("```")
            lines.append("")

    if migration_files:
        lines.append("## Konteks Migrasi")
        lines.append("")
        lines.append(
            "Migrasi membantu LLM memahami evolusi skema database, tetapi biasanya bukan sumber utama aturan bisnis."
        )
        lines.append("")
        for p in migration_files:
            rel = relative_str(feature_path, p)
            lines.append(f"### {rel}")
            lines.append("")
            lines.append("**Peran:** File migrasi database.")
            lines.append("")
            lines.append("```python")
            lines.append(clean_code_block(read_text_file(p)))
            lines.append("```")
            lines.append("")

    lines.append("## Catatan untuk LLM")
    lines.append("")
    lines.append("- Jangan menyimpulkan aturan bisnis hanya dari `views.py`; cek `services.py` dan `domain.py` terlebih dahulu.")
    lines.append("- Jangan mengubah kontrak response API tanpa memeriksa `tests/` dan `views.py`.")
    lines.append("- Untuk perubahan data, cek konsistensi antara `models.py`, `repositories.py`, dan `services.py`.")
    lines.append("- Untuk bug otorisasi, cek `permissions.py`, `views.py`, dan test terkait.")
    lines.append("- Untuk bug alur bisnis, cek urutan `domain.py -> services.py -> repositories.py -> tests/`.")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate markdown context modul Django agar mudah dibaca LLM."
    )
    parser.add_argument(
        "feature_path",
        help="Path ke folder feature, contoh: features/potensi_ekonomi",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Path file output markdown. Default: <feature_path>/llm_context.md",
    )
    args = parser.parse_args()

    feature_path = Path(args.feature_path).resolve()
    if not feature_path.exists() or not feature_path.is_dir():
        raise FileNotFoundError(f"Folder feature tidak ditemukan: {feature_path}")

    output_path = Path(args.output).resolve() if args.output else feature_path / "llm_context.md"

    project_root = feature_path.parent.parent if len(feature_path.parts) >= 2 else None
    markdown = build_markdown(feature_path=feature_path, project_root=project_root)

    output_path.write_text(markdown, encoding="utf-8")
    print(f"Berhasil membuat context file: {output_path}")


if __name__ == "__main__":
    main()
```

## Konteks Pengujian

Bagian ini penting untuk LLM karena test menunjukkan perilaku yang diharapkan, use case yang dijalankan, dan kontrak sistem yang harus dipertahankan.

### tests/__init__.py

**Peran:** File test untuk memverifikasi perilaku modul.

```python
# File kosong
```

## Konteks Migrasi

Migrasi membantu LLM memahami evolusi skema database, tetapi biasanya bukan sumber utama aturan bisnis.

### migrations/__init__.py

**Peran:** File migrasi database.

```python
# File kosong
```

## Catatan untuk LLM

- Jangan menyimpulkan aturan bisnis hanya dari `views.py`; cek `services.py` dan `domain.py` terlebih dahulu.
- Jangan mengubah kontrak response API tanpa memeriksa `tests/` dan `views.py`.
- Untuk perubahan data, cek konsistensi antara `models.py`, `repositories.py`, dan `services.py`.
- Untuk bug otorisasi, cek `permissions.py`, `views.py`, dan test terkait.
- Untuk bug alur bisnis, cek urutan `domain.py -> services.py -> repositories.py -> tests/`.
