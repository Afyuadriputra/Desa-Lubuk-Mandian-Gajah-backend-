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