from pathlib import Path
from datetime import datetime

# Jalankan script ini dari folder:
# D:\Kuliah\joki\radit\desa\backend\features

BASE_DIR = Path.cwd()
OUTPUT_FILE = BASE_DIR / "all_views_for_llm.md"

# Folder yang bukan feature
EXCLUDED_DIRS = {
    "__pycache__",
    "logs",
    "migrations",
    "tests",
    ".pytest_cache",
    ".git",
    ".venv",
    "env",
    "venv",
}


def is_feature_dir(path: Path) -> bool:
    """Feature dir harus berupa folder dan punya views.py"""
    return path.is_dir() and path.name not in EXCLUDED_DIRS and (path / "views.py").exists()


def read_file_safe(file_path: Path) -> str:
    """Baca file dengan fallback encoding"""
    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin-1"]
    for enc in encodings:
        try:
            return file_path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return file_path.read_text(errors="replace")


def build_output(feature_dirs: list[Path]) -> str:
    lines = []

    lines.append("# Django Views Collection for LLM")
    lines.append("")
    lines.append(f"Generated at: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"Base directory: `{BASE_DIR}`")
    lines.append("")
    lines.append("## Daftar Feature")
    lines.append("")

    for feature_dir in feature_dirs:
        lines.append(f"- `{feature_dir.name}`")

    lines.append("")
    lines.append("---")
    lines.append("")

    for i, feature_dir in enumerate(feature_dirs, start=1):
        views_file = feature_dir / "views.py"
        content = read_file_safe(views_file).rstrip()

        lines.append(f"## {i}. Feature: `{feature_dir.name}`")
        lines.append("")
        lines.append(f"**Path:** `{views_file}`")
        lines.append("")
        lines.append("```python")
        lines.append(content if content else "# views.py kosong")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main():
    feature_dirs = sorted(
        [p for p in BASE_DIR.iterdir() if is_feature_dir(p)],
        key=lambda p: p.name.lower()
    )

    if not feature_dirs:
        print("Tidak ada folder feature yang punya views.py")
        return

    output = build_output(feature_dirs)
    OUTPUT_FILE.write_text(output, encoding="utf-8")

    print(f"Berhasil mengumpulkan {len(feature_dirs)} views.py")
    print(f"Output disimpan di: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()