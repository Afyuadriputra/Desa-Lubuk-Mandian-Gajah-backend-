import os
from pathlib import Path

def generate_feature_context(target_dir="."):
    target_path = Path(target_dir).resolve()
    output_lines = []

    # 1. DAFTAR FILE PENTING (Berdasarkan list Anda)
    IMPORTANT_FILES = {
        "admin.py", "apps.py", "domain.py", "models.py", 
        "permissions.py", "repositories.py", "services.py", 
        "urls.py", "views.py", "__init__.py"
    }

    # Folder yang tetap harus diabaikan
    IGNORE_DIRS = {"__pycache__", "migrations", "env", "venv"}

    output_lines.append("================================================")
    output_lines.append(f"KONTEKS LOGIKA BISNIS: {target_path.name}")
    output_lines.append("================================================\n")

    # 2. EKSTRAKSI KODE
    for root, dirs, files in os.walk(target_path):
        # Filter folder sampah
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        current_dir = Path(root)
        
        # Urutkan file agar output rapi (domain dulu, baru service, baru view)
        files_to_read = [f for f in files if f in IMPORTANT_FILES]
        files_to_read.sort() 

        for file in files_to_read:
            file_path = current_dir / file
            rel_path = file_path.relative_to(target_path)

            # Lewati jika file kosong (seperti __init__.py yang biasanya nol)
            if file_path.stat().st_size == 0 and file != "__init__.py":
                continue

            output_lines.append("------------------------------------------------")
            output_lines.append(f"FILE: {rel_path}")
            output_lines.append("------------------------------------------------")

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if not content.strip():
                        output_lines.append(f"# [File {file} kosong atau hanya berisi komentar]\n")
                    else:
                        output_lines.append(content)
                        output_lines.append("\n")
            except Exception as e:
                output_lines.append(f"# [Gagal membaca {file}: {str(e)}]\n")

    return "\n".join(output_lines)

if __name__ == "__main__":
    # Script ini akan memproses folder tempat dia dijalankan
    print("Mengekstraksi kode penting untuk konteks LLM...")
    
    result = generate_feature_context(".")

    # Simpan ke file agar mudah di-copy
    output_filename = "konteks_feature_logic.txt"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(result)

    print("-" * 40)
    print(f"BERHASIL!")
    print(f"File '{output_filename}' telah dibuat.")
    print("Silakan copy isinya untuk memberikan konteks Clean Architecture ke LLM.")
    print("-" * 40)