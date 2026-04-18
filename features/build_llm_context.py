from pathlib import Path
from datetime import datetime

BASE_DIR = Path.cwd()
OUTPUT_DIR = BASE_DIR / "llm_contexts"

IMPORTANT_FILES_ORDER = [
    "apps.py",
    "models.py",
    "domain.py",
    "repositories.py",
    "services.py",
    "permissions.py",
    "schemas.py",
    "api.py",
    "views.py",
    "urls.py",
]

EXCLUDED_DIRS = {
    "__pycache__",
    "tests",
    "migrations",
    "logs",
    ".git",
    ".venv",
    "venv",
    "env",
    ".pytest_cache",
}

EXCLUDED_FILES = {
    "__init__.py",
    "collect_views.py",
    "build_llm_context.py",
    "build_llm_context_per_feature.py",
    "generate_llm_context.py",
    "llm_context.md",
    "all_views_for_llm.md",
    "all_views_for_llm.txt",
    "django_llm_context.md",
}


def read_file_safe(file_path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return file_path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return file_path.read_text(errors="replace")


def is_feature_dir(path: Path) -> bool:
    if not path.is_dir():
        return False
    if path.name in EXCLUDED_DIRS:
        return False

    return any((path / name).exists() for name in IMPORTANT_FILES_ORDER)


def collect_feature_files(feature_dir: Path) -> list[Path]:
    files = []
    for filename in IMPORTANT_FILES_ORDER:
        fp = feature_dir / filename
        if fp.exists() and fp.is_file() and fp.name not in EXCLUDED_FILES:
            files.append(fp)
    return files


def build_feature_markdown(feature_dir: Path, feature_files: list[Path]) -> str:
    lines = []

    lines.append(f"# Feature Context: {feature_dir.name}")
    lines.append("")
    lines.append(f"Generated at: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"Feature path: `{feature_dir}`")
    lines.append("")
    lines.append("Dokumen ini berisi layer penting untuk konteks LLM.")
    lines.append("Folder `tests`, `migrations`, `logs`, dan file non-konteks tidak disertakan.")
    lines.append("")

    if not feature_files:
        lines.append("_Tidak ada file penting yang ditemukan._")
        lines.append("")
        return "\n".join(lines)

    lines.append("## Included Layers")
    lines.append("")
    for f in feature_files:
        lines.append(f"- `{f.name}`")
    lines.append("")
    lines.append("---")
    lines.append("")

    for f in feature_files:
        content = read_file_safe(f).rstrip()

        lines.append(f"## File: `{f.name}`")
        lines.append("")
        lines.append("```python")
        lines.append(content if content else "# file kosong")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    feature_dirs = sorted(
        [p for p in BASE_DIR.iterdir() if is_feature_dir(p)],
        key=lambda p: p.name.lower()
    )

    if not feature_dirs:
        print("Tidak ditemukan feature yang berisi layer penting.")
        return

    generated_files = []

    for feature_dir in feature_dirs:
        feature_files = collect_feature_files(feature_dir)
        markdown = build_feature_markdown(feature_dir, feature_files)

        output_file = OUTPUT_DIR / f"{feature_dir.name}.md"
        output_file.write_text(markdown, encoding="utf-8")
        generated_files.append(output_file)

    print(f"Berhasil membuat {len(generated_files)} file konteks feature.")
    print(f"Output directory: {OUTPUT_DIR}")
    print("Daftar file:")
    for f in generated_files:
        print(f" - {f.name}")


if __name__ == "__main__":
    main()