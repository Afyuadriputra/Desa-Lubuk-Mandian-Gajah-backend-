import os
from pathlib import Path

def generate_llm_context(target_dir="."):
    target_path = Path(target_dir).resolve()
    output_lines = []

    # 1. KONFIGURASI FILTERING (Hanya mengambil yang penting)
    IGNORE_DIRS = {
        "env", "venv", "__pycache__", ".git", "logs", ".vscode", ".idea", "migrations"
    }
    IGNORE_FILES = {
        ".env", "db.sqlite3", "generate_context.py", "konteks_llm.txt", ".gitignore"
    }
    IGNORE_EXTENSIONS = {
        ".pyc", ".pyo", ".log", ".sqlite3", ".jpg", ".png", ".pdf", ".zip"
    }

    output_lines.append("================================================")
    output_lines.append("1. STRUKTUR ARSITEKTUR PROJECT")
    output_lines.append("================================================")
    output_lines.append(f"Project Root: {target_path.name}\n")

    # Fungsi rekursif untuk menggambar Tree
    def walk_tree(dir_path, prefix=""):
        try:
            paths = sorted(dir_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except PermissionError:
            return

        # Menyaring direktori dan file
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
    output_lines.append("2. ISI KODE RELEVAN")
    output_lines.append("================================================")

    # Membaca isi file yang lolos filter
    for root, dirs, files in os.walk(target_path):
        # Modifikasi list dirs (in-place) agar os.walk tidak masuk ke folder sampah
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        current_dir = Path(root)
        valid_files = [
            f for f in files 
            if f not in IGNORE_FILES 
            and not any(f.endswith(ext) for ext in IGNORE_EXTENSIONS)
        ]

        for file in sorted(valid_files):
            file_path = current_dir / file
            rel_path = file_path.relative_to(target_path)

            # Lewati file kosong (0 bytes) agar konteks LLM tidak penuh sampah
            if file_path.stat().st_size == 0:
                continue

            output_lines.append("------------------------------------------------")
            output_lines.append(f"FILE: {rel_path}")
            output_lines.append("------------------------------------------------")

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if not content.strip():
                        output_lines.append("[PEMBERITAHUAN: FILE INI HANYA BERISI SPASI/ENTER]\n")
                    else:
                        output_lines.append(content)
                        output_lines.append("\n")
            except Exception:
                output_lines.append(f"[PEMBERITAHUAN: GAGAL MEMBACA FILE - BUKAN TEKS]\n")

    return "\n".join(output_lines)

if __name__ == "__main__":
    print("Menganalisis arsitektur project...")
    target_directory = "."  # Otomatis menggunakan direktori tempat script ini berada

    result = generate_llm_context(target_directory)

    # Menyimpan hasil ke file teks
    output_file = "konteks_llm.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"Selesai! File yang diabaikan: env, logs, db.sqlite3, .env, dll.")
    print(f"Hasil ekstraksi kode telah disimpan dengan bersih di: {output_file}")
    