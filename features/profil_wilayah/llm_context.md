# Context Modul: profil_wilayah

## Tujuan Dokumen

Dokumen ini dibuat untuk membantu LLM memahami konteks modul secara akurat. Struktur disusun berdasarkan peran file dalam arsitektur Django modular berbasis feature.

## Metadata

- Nama modul: `profil_wilayah`
- Path modul: `D:/Kuliah/joki/radit/desa/backend/features/profil_wilayah`
- Digenerate pada: `2026-04-18 23:47:50`

## Panduan Membaca Modul untuk LLM

- `domain.py` berisi aturan bisnis murni dan validasi inti.
- `models.py` berisi struktur data yang tersimpan di database.
- `repositories.py` berisi akses data dan query persistence.
- `services.py` berisi use case dan orkestrasi alur bisnis.
- `permissions.py` berisi aturan otorisasi.
- `views.py` berisi antarmuka HTTP/API.
- `urls.py` menghubungkan route ke view.
- `tests/` menunjukkan perilaku yang diharapkan sistem.
- `migrations/` menunjukkan evolusi skema database.

Saat menganalisis bug atau membuat fitur baru, prioritaskan pembacaan file dalam urutan: `domain.py -> models.py -> repositories.py -> services.py -> permissions.py -> views.py -> urls.py -> tests/`.

## Struktur File

- `apps.py`
- `domain.py`
- `models.py`
- `permissions.py`
- `repositories.py`
- `services.py`
- `admin.py`
- `__init__.py`
- `api.py`
- `generate_llm_context.py`
- `get_profil_context.py`
- `schemas.py`
- `tests/__init__.py`
- `tests/test_api.py`
- `tests/test_domain.py`
- `tests/test_repositories.py`
- `tests/test_services.py`
- `migrations/0001_initial.py`
- `migrations/__init__.py`

## Ringkasan Layer

- `apps.py`: Konfigurasi Django app untuk modul ini.
- `domain.py`: Aturan bisnis murni, validasi domain, konstanta, helper bisnis, dan logika yang tidak bergantung pada framework.
- `models.py`: Definisi model database Django, relasi antar entitas, field, dan perilaku model.
- `permissions.py`: Aturan otorisasi dan hak akses terhadap resource atau aksi di modul ini.
- `repositories.py`: Lapisan akses data untuk query, penyimpanan, update, atau abstraksi interaksi database.
- `services.py`: Use case / application service. Mengorkestrasi domain, repository, validasi, side effects, dan flow bisnis utama.
- `admin.py`: Konfigurasi Django admin untuk model dalam modul ini.
- `__init__.py`: Penanda package Python. Biasanya minim logika.
- `api.py`: File tambahan pada modul.
- `generate_llm_context.py`: File tambahan pada modul.
- `get_profil_context.py`: File tambahan pada modul.
- `schemas.py`: File tambahan pada modul.
- `tests/`: Skenario verifikasi perilaku sistem pada modul.
- `migrations/`: Riwayat perubahan skema database.

## Konteks Kode per File

### apps.py

**Peran:** Konfigurasi Django app untuk modul ini.

```python
from django.apps import AppConfig


class ProfilWilayahConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'features.profil_wilayah'
```

### domain.py

**Peran:** Aturan bisnis murni, validasi domain, konstanta, helper bisnis, dan logika yang tidak bergantung pada framework.

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

### models.py

**Peran:** Definisi model database Django, relasi antar entitas, field, dan perilaku model.

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

### permissions.py

**Peran:** Aturan otorisasi dan hak akses terhadap resource atau aksi di modul ini.

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

### repositories.py

**Peran:** Lapisan akses data untuk query, penyimpanan, update, atau abstraksi interaksi database.

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

### services.py

**Peran:** Use case / application service. Mengorkestrasi domain, repository, validasi, side effects, dan flow bisnis utama.

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

### admin.py

**Peran:** Konfigurasi Django admin untuk model dalam modul ini.

```python
from django.contrib import admin
from features.profil_wilayah.models import WilayahDusun, WilayahPerangkat, ProfilDesa

@admin.register(WilayahDusun)
class WilayahDusunAdmin(admin.ModelAdmin):
    list_display = ("nama_dusun", "kepala_dusun", "created_at")
    search_fields = ("nama_dusun", "kepala_dusun")

@admin.register(WilayahPerangkat)
class WilayahPerangkatAdmin(admin.ModelAdmin):
    list_display = ("user", "jabatan", "is_published", "created_at")
    list_filter = ("is_published",)
    search_fields = ("user__nama_lengkap", "jabatan")

@admin.register(ProfilDesa)
class ProfilDesaAdmin(admin.ModelAdmin):
    list_display = ("id", "updated_at")
    # Karena Profil Desa konsepnya YAGNI/Singleton (hanya 1 row), 
    # kita tidak perlu filter atau search yang rumit.
```

### __init__.py

**Peran:** Penanda package Python. Biasanya minim logika.

```python
# File kosong
```

## File Tambahan

### api.py

**Peran:** File tambahan pada modul.

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

IGNORED_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".git",
    "venv",
    "env",
}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


def read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")
    except Exception as exc:
        return f"# Gagal membaca file: {exc}"


def clean_code_block(text: str) -> str:
    text = text.rstrip()
    return text if text else "# File kosong"


def ordered_main_files(feature_path: Path) -> list[Path]:
    result = []
    for name in DEFAULT_ORDER:
        p = feature_path / name
        if p.exists() and p.is_file():
            result.append(p)
    return result


def collect_extra_python_files(feature_path: Path) -> list[Path]:
    main_files = {p.resolve() for p in ordered_main_files(feature_path)}
    result = []

    for p in feature_path.rglob("*.py"):
        if any(part in IGNORED_DIRS for part in p.parts):
            continue
        if p.suffix in IGNORED_SUFFIXES:
            continue
        if p.resolve() in main_files:
            continue
        if "migrations" in p.parts or "tests" in p.parts:
            continue
        result.append(p)

    return sorted(result)


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


def build_markdown(feature_path: Path) -> str:
    feature_name = feature_path.name
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    main_files = ordered_main_files(feature_path)
    extra_files = collect_extra_python_files(feature_path)
    test_files = collect_test_files(feature_path)
    migration_files = collect_migration_files(feature_path)

    lines: list[str] = []

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
    lines.append("- `migrations/` menunjukkan evolusi skema database.")
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
    for p in extra_files:
        lines.append(f"- `{relative_str(feature_path, p)}`")
    for p in test_files:
        lines.append(f"- `{relative_str(feature_path, p)}`")
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
        nargs="?",
        default=".",
        help="Path ke folder feature. Default: folder saat ini.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="llm_context.md",
        help="Nama/path file output markdown. Default: llm_context.md",
    )
    args = parser.parse_args()

    feature_path = Path(args.feature_path).resolve()
    if not feature_path.exists() or not feature_path.is_dir():
        raise FileNotFoundError(f"Folder feature tidak ditemukan: {feature_path}")

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = feature_path / output_path

    markdown = build_markdown(feature_path)
    output_path.write_text(markdown, encoding="utf-8")

    print(f"Berhasil membuat context file: {output_path}")


if __name__ == "__main__":
    main()
```

### get_profil_context.py

**Peran:** File tambahan pada modul.

```python
import os

def build_feature_context(feature_path, target_files, output_name):
    """
    Mengambil file spesifik dari sebuah fitur untuk konteks LLM.
    """
    # Pastikan path menggunakan format yang benar untuk OS (Windows/Linux)
    feature_dir = os.path.normpath(feature_path)
    feature_name = os.path.basename(feature_dir)
    
    if not os.path.exists(feature_dir):
        print(f"❌ Error: Folder {feature_dir} tidak ditemukan.")
        return

    print(f"📂 Memproses Fitur: {feature_name}")
    
    with open(output_name, "w", encoding="utf-8") as out_f:
        out_f.write(f"# Context LLM: Fitur {feature_name}\n")
        out_f.write(f"Lokasi: `{feature_path}`\n\n")
        
        for file_name in target_files:
            file_path = os.path.join(feature_dir, file_name)
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as in_f:
                        content = in_f.read()
                    
                    # Menulis ke Markdown
                    out_f.write(f"---\n## File: `{feature_name}/{file_name}`\n\n")
                    out_f.write(f"```python\n")
                    out_f.write(content)
                    out_f.write(f"\n```\n\n")
                    print(f"✅ Berhasil mengambil: {file_name}")
                    
                except Exception as e:
                    print(f"⚠️ Gagal membaca {file_name}: {e}")
            else:
                # Karena kamu bilang "kalau ada", kita buat log saja jika tidak ada
                print(f"ℹ️ Skip: {file_name} (Tidak ditemukan)")

if __name__ == "__main__":
    # Path folder fitur
    PROFIL_PATH = "profil_wilayah" 
    
    # List file yang kamu minta
    FILES_TO_GET = [
        "api.py",
        "services.py",
        "repositories.py",
        "models.py",
        "permissions.py",
        "urls.py",
        "schemas.py" # Tambahan jika diperlukan karena biasanya ada di Ninja/FastAPI
    ]
    
    OUTPUT_FILE = "context_profil_wilayah.md"
    
    build_feature_context(PROFIL_PATH, FILES_TO_GET, OUTPUT_FILE)
    print(f"\n✨ Selesai! Konteks disimpan di: {OUTPUT_FILE}")
```

### schemas.py

**Peran:** File tambahan pada modul.

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

## Konteks Pengujian

Bagian ini penting untuk LLM karena test menunjukkan perilaku yang diharapkan, use case yang dijalankan, dan kontrak sistem yang harus dipertahankan.

### tests/__init__.py

**Peran:** File test untuk memverifikasi perilaku modul.

```python
# File kosong
```

### tests/test_api.py

**Peran:** File test untuk memverifikasi perilaku modul.

```python
import pytest
import json
from features.profil_wilayah.models import ProfilDesa

@pytest.mark.django_db
class TestProfilWilayahAPI:

    def test_publik_bisa_akses_tanpa_login_dan_teragregasi(self, client):
        """KISS: Menguji bahwa endpoint /publik mengembalikan Profil dan Perangkat tanpa auth."""
        # Setup data
        ProfilDesa.objects.create(id=1, visi="Visi API", misi="Misi API", sejarah="Sejarah API")
        
        # Request tanpa force_login
        response = client.get("/api/v1/profil-wilayah/publik")
        
        assert response.status_code == 200
        data = response.json()
        
        # Cek struktur aggregated
        assert "profil" in data
        assert "perangkat" in data
        assert data["profil"]["visi"] == "Visi API"

    def test_update_profil_dengan_xss_otomatis_bersih(self, client, admin_user):
        """DRY: Menguji SafeHTMLString pada JSON Payload."""
        client.force_login(admin_user)
        
        # Pydantic via JSON body
        payload = {
            "visi": "<b>Visi Hebat</b>",
            "misi": "Misi Kuat",
            "sejarah": "<script>console.log('xss')</script> Sejarah lama"
        }

        response = client.put(
            "/api/v1/profil-wilayah/admin/profil", 
            data=json.dumps(payload), 
            content_type="application/json"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "<b>Visi Hebat</b>" in data["visi"]
        assert "<script>" not in data["sejarah"] # XSS hilang
        assert "Sejarah lama" in data["sejarah"]
```

### tests/test_domain.py

**Peran:** File test untuk memverifikasi perilaku modul.

```python
import pytest
from features.profil_wilayah.domain import (
    InvalidDataError,
    validate_dusun,
    validate_perangkat,
    validate_profil_desa,
)

class TestDomainProfilWilayah:
    # --- Validasi Dusun ---
    def test_validasi_dusun_harus_sukses_jika_data_valid(self):
        validate_dusun(nama_dusun="Mawar", kepala_dusun="Pak Budi")  # Tidak boleh error

    def test_validasi_dusun_harus_gagal_jika_nama_terlalu_pendek(self):
        with pytest.raises(InvalidDataError, match="minimal 3 karakter"):
            validate_dusun(nama_dusun="AB", kepala_dusun="Pak Budi")

    def test_validasi_dusun_harus_gagal_jika_kepala_dusun_kosong(self):
        with pytest.raises(InvalidDataError, match="kepala dusun wajib diisi"):
            validate_dusun(nama_dusun="Melati", kepala_dusun="   ")

    # --- Validasi Perangkat ---
    def test_validasi_perangkat_harus_sukses_jika_jabatan_valid(self):
        validate_perangkat(jabatan="Sekretaris Desa")

    def test_validasi_perangkat_harus_gagal_jika_jabatan_kosong(self):
        with pytest.raises(InvalidDataError, match="Jabatan wajib diisi"):
            validate_perangkat(jabatan="")

    # --- Validasi Profil Desa ---
    def test_validasi_profil_desa_harus_sukses_jika_lengkap(self):
        validate_profil_desa(visi="Maju", misi="Bersama", sejarah="Tahun 1990")

    def test_validasi_profil_desa_harus_gagal_jika_ada_yang_kosong(self):
        with pytest.raises(InvalidDataError, match="tidak boleh kosong"):
            validate_profil_desa(visi="Maju", misi="", sejarah="Tahun 1990")
```

### tests/test_repositories.py

**Peran:** File test untuk memverifikasi perilaku modul.

```python
import pytest
from features.profil_wilayah.repositories import (
    DusunRepository,
    PerangkatRepository,
    ProfilDesaRepository,
)

pytestmark = pytest.mark.django_db

class TestProfilWilayahRepositories:
    def test_profil_desa_repo_harus_implementasi_singleton(self):
        """Memastikan get_profil() selalu mengembalikan record dengan ID=1 (YAGNI)."""
        repo = ProfilDesaRepository()
        
        profil_1 = repo.get_profil()
        profil_2 = repo.get_profil()
        
        assert profil_1.id == 1
        assert profil_1.id == profil_2.id

    def test_profil_desa_repo_harus_bisa_update_data(self):
        repo = ProfilDesaRepository()
        updated_profil = repo.update_profil(visi="Visi Baru", misi="Misi Baru", sejarah="Sejarah Baru")
        
        assert updated_profil.visi == "Visi Baru"
        
        # Pastikan data tersimpan di DB
        db_profil = repo.get_profil()
        assert db_profil.visi == "Visi Baru"

    def test_perangkat_repo_hanya_kembalikan_yang_dipublish(self, django_user_model):
        user = django_user_model.objects.create(nik="123", nama_lengkap="Warga")
        repo = PerangkatRepository()
        
        repo.create(user_id=user.id, jabatan="Kaur", is_published=True)
        repo.create(user_id=user.id, jabatan="Kasi", is_published=False)
        
        hasil = repo.list_published()
        assert hasil.count() == 1
        assert hasil.first().jabatan == "Kaur"
```

### tests/test_services.py

**Peran:** File test untuk memverifikasi perilaku modul.

```python
import pytest
from features.profil_wilayah.services import (
    DusunService,
    ProfilWilayahAccessError,
)

class TestDusunService:
    @pytest.fixture
    def mock_repo(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def service(self, mock_repo):
        # Menerapkan Dependency Inversion dengan meng-inject Mock Repository
        return DusunService(repo=mock_repo)

    @pytest.fixture
    def mock_admin(self, mocker):
        user = mocker.Mock(id=1, role="ADMIN")
        return user

    def test_tambah_dusun_harus_sukses_untuk_admin(self, service, mock_admin, mock_repo, mocker):
        # Arrange
        mocker.patch("features.profil_wilayah.services.can_manage_data_wilayah", return_value=True)
        mock_audit = mocker.patch("features.profil_wilayah.services.audit_event")
        mock_repo.create.return_value = mocker.Mock(id=10)

        # Act
        hasil = service.tambah_dusun(mock_admin, nama_dusun="Mawar", kepala_dusun="Budi")

        # Assert
        assert hasil.id == 10
        mock_repo.create.assert_called_once_with("Mawar", "Budi")
        mock_audit.assert_called_once_with("DUSUN_CREATED", actor_id=1, target_id=10)

    def test_tambah_dusun_harus_ditolak_jika_tidak_punya_izin(self, service, mock_admin, mocker):
        mocker.patch("features.profil_wilayah.services.can_manage_data_wilayah", return_value=False)

        with pytest.raises(ProfilWilayahAccessError, match="Akses ditolak"):
            service.tambah_dusun(mock_admin, nama_dusun="Mawar", kepala_dusun="Budi")
```

## Konteks Migrasi

Migrasi membantu LLM memahami evolusi skema database, tetapi biasanya bukan sumber utama aturan bisnis.

### migrations/0001_initial.py

**Peran:** File migrasi database.

```python
# Generated by Django 5.0.3 on 2026-04-17 02:13

import django.db.models.deletion
import django.utils.timezone
import toolbox.storage.paths
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfilDesa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visi', models.TextField()),
                ('misi', models.TextField()),
                ('sejarah', models.TextField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'profil_desa',
            },
        ),
        migrations.CreateModel(
            name='WilayahDusun',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('nama_dusun', models.CharField(max_length=100)),
                ('kepala_dusun', models.CharField(max_length=150)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'wilayah_dusun',
            },
        ),
        migrations.CreateModel(
            name='WilayahPerangkat',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('jabatan', models.CharField(max_length=100)),
                ('foto', models.ImageField(blank=True, null=True, upload_to=toolbox.storage.paths.perangkat_photo_upload_path)),
                ('is_published', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'wilayah_perangkat',
            },
        ),
    ]
```

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
