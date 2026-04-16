import os
from pathlib import Path

def generate_clean_architecture_context(target_dir="."):
    target_path = Path(target_dir).resolve()
    output_lines = []

    # 1. DAFTAR PENGABAIAN (Ignore List)
    IGNORE_DIRS = {
        "env", "venv", "__pycache__", ".git", "logs", 
        "migrations", ".pytest_cache", "afyu", ".vscode", ".idea"
    }
    IGNORE_FILES = {
        ".env", ".env.example", "db.sqlite3", "generate_context_arsitektur.py", 
        "konteks_llm.txt", ".gitignore", "pytest.ini", "requirements.txt"
    }
    IGNORE_EXTENSIONS = {
        ".pyc", ".log", ".sqlite3", ".jpg", ".png", ".pdf", ".zip", ".md"
    }

    # 2. FILE PRIORITAS CLEAN ARCHITECTURE
    # Hanya file ini yang akan dibaca isinya untuk menjaga konteks LLM tetap relevan
    IMPORTANT_FILES = {
        "domain.py", "models.py", "repositories.py", "services.py", 
        "views.py", "urls.py", "permissions.py", "admin.py", 
        "apps.py", "tests.py", "manage.py", "app_logger.py", "request_context.py"
    }

    output_lines.append("================================================")
    output_lines.append("1. STRUKTUR ARSITEKTUR PROJECT")
    output_lines.append("================================================")
    output_lines.append(f"Project Root: {target_path.name}\n")

    def walk_tree(dir_path, prefix=""):
        try:
            paths = sorted(dir_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except PermissionError:
            return

        valid_paths = [
            p for p in paths 
            if p.name not in IGNORE_DIRS 
            and p.name not in IGNORE_FILES 
            and p.suffix.lower() not in IGNORE_EXTENSIONS
        ]

        count = len(valid_paths)
        for i, p in enumerate(valid_paths):
            is_last = (i == count - 1)
            connector = "└─── " if is_last else "├─── "
            output_lines.append(prefix + connector + p.name)

            if p.is_dir():
                extension = "    " if is_last else "│   "
                walk_tree(p, prefix + extension)

    walk_tree(target_path)
    output_lines.append("\n")

    output_lines.append("================================================")
    output_lines.append("2. KODE LOGIKA BISNIS & ARSITEKTUR")
    output_lines.append("================================================")

    for root, dirs, files in os.walk(target_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        current_dir = Path(root)
        
        # Urutkan file berdasarkan prioritas (Domain -> Repo -> Service -> View)
        files_to_read = [f for f in files if f in IMPORTANT_FILES]
        files_to_read.sort(key=lambda x: (
            0 if x == "domain.py" else
            1 if x == "models.py" else
            2 if x == "repositories.py" else
            3 if x == "services.py" else
            4 if x == "views.py" else
            5 if x == "urls.py" else 10
        ))

        for file in files_to_read:
            file_path = current_dir / file
            rel_path = file_path.relative_to(target_path)

            if file_path.stat().st_size == 0:
                continue

            output_lines.append("------------------------------------------------")
            output_lines.append(f"FILE: {rel_path}")
            output_lines.append("------------------------------------------------")

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if not content.strip():
                        output_lines.append("[KOSONG ATAU HANYA KOMENTAR]\n")
                    else:
                        output_lines.append(content)
                        output_lines.append("\n")
            except Exception:
                output_lines.append("[GAGAL MEMBACA FILE]\n")

    return "\n".join(output_lines)

if __name__ == "__main__":
    print("Mengekstraksi struktur dan kode Clean Architecture...")
    result = generate_clean_architecture_context(".")

    output_file = "konteks_llm.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"Selesai! Konteks berhasil diperbarui ke dalam '{output_file}'.")