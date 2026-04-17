# Context Modul: publikasi_informasi

## Tujuan Dokumen

Dokumen ini dibuat untuk membantu LLM memahami konteks modul secara akurat. Struktur disusun berdasarkan peran file dalam arsitektur Django modular berbasis feature.

## Metadata

- Nama modul: `publikasi_informasi`
- Path modul: `D:/Kuliah/joki/radit/desa/backend/features/publikasi_informasi`
- Digenerate pada: `2026-04-17 09:42:29`

## Panduan Membaca Modul untuk LLM

- `domain.py` berisi aturan bisnis murni dan validasi inti.
- `models.py` berisi struktur data yang tersimpan di database.
- `repositories.py` berisi akses data dan query persistence.
- `services.py` berisi use case dan orkestrasi alur bisnis.
- `permissions.py` berisi aturan otorisasi.
- `views.py` berisi antarmuka HTTP atau API.
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
- `views.py`
- `urls.py`
- `admin.py`
- `__init__.py`
- `generate_llm_context.py`
- `tests/__init__.py`
- `migrations/0001_initial.py`
- `migrations/__init__.py`

## Ringkasan Layer

- `apps.py`: Konfigurasi Django app untuk modul ini.
- `domain.py`: Aturan bisnis murni, validasi domain, konstanta, helper bisnis, dan logika yang tidak bergantung pada framework.
- `models.py`: Definisi model database Django, relasi antar entitas, field, dan perilaku model.
- `permissions.py`: Aturan otorisasi dan hak akses terhadap resource atau aksi di modul ini.
- `repositories.py`: Lapisan akses data untuk query, penyimpanan, update, atau abstraksi interaksi database.
- `services.py`: Use case atau application service. Mengorkestrasi domain, repository, validasi, side effect, dan flow bisnis utama.
- `views.py`: Lapisan HTTP atau API. Menerima request, memanggil service, menerapkan permission, dan mengembalikan response.
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


class PublikasiInformasiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'features.publikasi_informasi'
```

### domain.py

**Peran:** Aturan bisnis murni, validasi domain, konstanta, helper bisnis, dan logika yang tidak bergantung pada framework.

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

### models.py

**Peran:** Definisi model database Django, relasi antar entitas, field, dan perilaku model.

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

### permissions.py

**Peran:** Aturan otorisasi dan hak akses terhadap resource atau aksi di modul ini.

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

### repositories.py

**Peran:** Lapisan akses data untuk query, penyimpanan, update, atau abstraksi interaksi database.

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

### services.py

**Peran:** Use case atau application service. Mengorkestrasi domain, repository, validasi, side effect, dan flow bisnis utama.

```python
# features/publikasi_informasi/services.py

from django.utils import timezone
from features.publikasi_informasi.domain import (
    PublikasiError, validate_publikasi_input, STATUS_PUBLISHED, STATUS_DRAFT
)
from features.publikasi_informasi.permissions import can_create_or_edit_publikasi
from features.publikasi_informasi.repositories import PublikasiRepository
from toolbox.logging import audit_event
from toolbox.security.sanitizers import sanitize_rich_text_content

class PublikasiAccessError(Exception):
    pass

class PublikasiService:
    # Dependency Inversion: Repository diinjeksi
    def __init__(self, repo: PublikasiRepository = None):
        self.repo = repo or PublikasiRepository()

    def buat_publikasi(self, actor, judul: str, konten_html: str, jenis: str, status: str):
        if not can_create_or_edit_publikasi(actor):
            raise PublikasiAccessError("Anda tidak memiliki izin mengelola publikasi.")

        validate_publikasi_input(judul, konten_html, jenis, status)

        # SANITASI HTML: Mencegah XSS Attack dari input WYSIWYG Editor Frontend
        clean_html = sanitize_rich_text_content(konten_html)

        published_at = timezone.now() if status == STATUS_PUBLISHED else None

        publikasi = self.repo.create({
            "judul": judul.strip(),
            "konten_html": clean_html,
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

### views.py

**Peran:** Lapisan HTTP atau API. Menerima request, memanggil service, menerapkan permission, dan mengembalikan response.

```python
# features/publikasi_informasi/views.py

import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from features.publikasi_informasi.services import PublikasiService, PublikasiError, PublikasiAccessError
from toolbox.security.auth import is_active_user

publikasi_service = PublikasiService()

@require_GET
def list_publikasi_publik_view(request):
    jenis = request.GET.get("jenis") # Opsional: ?jenis=BERITA
    qs = publikasi_service.get_publikasi_publik(jenis)
    data = [{
        "judul": p.judul, 
        "slug": p.slug, 
        "jenis": p.jenis,
        "penulis": p.penulis.nama_lengkap if p.penulis else "Admin",
        "published_at": p.published_at.isoformat() if p.published_at else None
    } for p in qs]
    return JsonResponse({"data": data}, status=200)

@require_GET
def detail_publikasi_view(request, slug):
    try:
        p = publikasi_service.get_detail_publik(slug)
        return JsonResponse({
            "data": {
                "judul": p.judul,
                "konten_html": p.konten_html, # Aman, sudah disanitasi saat disave
                "jenis": p.jenis,
                "penulis": p.penulis.nama_lengkap if p.penulis else "Admin",
                "published_at": p.published_at.isoformat() if p.published_at else None
            }
        }, status=200)
    except PublikasiError as e:
        return JsonResponse({"detail": str(e)}, status=404)

@require_POST
def buat_publikasi_admin_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor): 
        return JsonResponse({"detail": "Unauthorized"}, status=401)
        
    data = json.loads(request.body.decode("utf-8") or "{}")
    try:
        publikasi = publikasi_service.buat_publikasi(
            actor=actor,
            judul=data.get("judul"),
            konten_html=data.get("konten_html"),
            jenis=data.get("jenis", "BERITA"),
            status=data.get("status", "DRAFT")
        )
        return JsonResponse({"detail": "Publikasi berhasil dibuat", "slug": publikasi.slug}, status=201)
    except (PublikasiError, PublikasiAccessError) as e:
        return JsonResponse({"detail": str(e)}, status=400)
```

### urls.py

**Peran:** Pemetaan endpoint URL ke views.

```python
# features/publikasi_informasi/urls.py

from django.urls import path
from features.publikasi_informasi.views import (
    list_publikasi_publik_view, 
    detail_publikasi_view, 
    buat_publikasi_admin_view
)

urlpatterns = [
    path("publikasi/", list_publikasi_publik_view, name="publikasi-list-publik"),
    path("publikasi/admin/buat/", buat_publikasi_admin_view, name="publikasi-admin-buat"),
    path("publikasi/<slug:slug>/", detail_publikasi_view, name="publikasi-detail"),
]
```

### admin.py

**Peran:** Konfigurasi Django admin untuk model dalam modul ini.

```python
# features/publikasi_informasi/admin.py

from django.contrib import admin
from features.publikasi_informasi.models import Publikasi

@admin.register(Publikasi)
class PublikasiAdmin(admin.ModelAdmin):
    list_display = ("judul", "jenis", "status", "published_at")
    list_filter = ("jenis", "status")
    search_fields = ("judul",)
    readonly_fields = ("slug", "created_at", "updated_at")
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
    "services.py": "Use case atau application service. Mengorkestrasi domain, repository, validasi, side effect, dan flow bisnis utama.",
    "views.py": "Lapisan HTTP atau API. Menerima request, memanggil service, menerapkan permission, dan mengembalikan response.",
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
    lines.append("- `views.py` berisi antarmuka HTTP atau API.")
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

## Konteks Pengujian

Bagian ini penting untuk LLM karena test menunjukkan perilaku yang diharapkan, use case yang dijalankan, dan kontrak sistem yang harus dipertahankan.

### tests/__init__.py

**Peran:** File test untuk memverifikasi perilaku modul.

```python
# File kosong
```

## Konteks Migrasi

Migrasi membantu LLM memahami evolusi skema database, tetapi biasanya bukan sumber utama aturan bisnis.

### migrations/0001_initial.py

**Peran:** File migrasi database.

```python
# Generated by Django 5.0.3 on 2026-04-17 02:40

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Publikasi',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('judul', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=220, unique=True)),
                ('konten_html', models.TextField()),
                ('jenis', models.CharField(choices=[('BERITA', 'BERITA'), ('PENGUMUMAN', 'PENGUMUMAN')], default='BERITA', max_length=20)),
                ('status', models.CharField(choices=[('PUBLISHED', 'PUBLISHED'), ('DRAFT', 'DRAFT')], default='DRAFT', max_length=20)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('penulis', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'publikasi_informasi',
                'ordering': ['-published_at', '-created_at'],
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
