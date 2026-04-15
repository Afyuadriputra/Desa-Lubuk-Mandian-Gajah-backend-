import os
from pathlib import Path

def generate_llm_context(target_dir="."):
    target_path = Path(target_dir).resolve()
    output_lines = []

    # File dan folder yang akan diabaikan
    IGNORE_DIRS = {"__pycache__", "env", ".git", "venv"}
    IGNORE_FILES = {"semua_kode_toolbox.txt", "konteks_llm.txt"}
    IGNORE_EXTENSIONS = {".pyc", ".pyo"}

    output_lines.append("================================================")
    output_lines.append("1. STRUKTUR FOLDER")
    output_lines.append("================================================")
    output_lines.append(str(target_path))

    # Fungsi rekursif untuk menggambar Tree
    def walk_tree(dir_path, prefix=""):
        try:
            # Urutkan: Folder lebih dulu, baru file
            paths = sorted(dir_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except PermissionError:
            return

        # Filter file/folder yang tidak diinginkan
        valid_paths = [
            p for p in paths 
            if p.name not in IGNORE_DIRS 
            and p.name not in IGNORE_FILES 
            and p.suffix not in IGNORE_EXTENSIONS
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
    output_lines.append("2. ISI KODE FILE")
    output_lines.append("================================================")

    # Membaca isi file dan mengecek direktori kosong
    for root, dirs, files in os.walk(target_path):
        # Modifikasi list dirs (in-place) agar os.walk tidak masuk ke folder ignore
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        current_dir = Path(root)

        # Cek folder kosong
        valid_files = [f for f in files if f not in IGNORE_FILES and not any(f.endswith(ext) for ext in IGNORE_EXTENSIONS)]
        if not dirs and not valid_files:
            if current_dir != target_path:
                rel_dir = current_dir.relative_to(target_path)
                output_lines.append("------------------------------------------------")
                output_lines.append(f"FOLDER: {rel_dir}")
                output_lines.append("------------------------------------------------")
                output_lines.append("[PEMBERITAHUAN: FOLDER INI KOSONG]\n")

        # Cek isi file
        for file in sorted(valid_files):
            file_path = current_dir / file
            rel_path = file_path.relative_to(target_path)

            output_lines.append("------------------------------------------------")
            output_lines.append(f"FILE: {rel_path}")
            output_lines.append("------------------------------------------------")

            # Cek ukuran file 0 bytes
            if file_path.stat().st_size == 0:
                output_lines.append("[PEMBERITAHUAN: FILE INI KOSONG (0 BYTES)]\n")
            else:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        # Cek jika file hanya berisi spasi/enter
                        if not content.strip():
                            output_lines.append("[PEMBERITAHUAN: FILE INI HANYA BERISI SPASI ATAU ENTER]\n")
                        else:
                            output_lines.append(content)
                            output_lines.append("\n")
                except Exception as e:
                    output_lines.append(f"[PEMBERITAHUAN: GAGAL MEMBACA FILE - BUKAN FILE TEKS]\n")

    return "\n".join(output_lines)

if __name__ == "__main__":
    # Ganti path ini ke direktori yang ingin Anda scan, contoh: r"D:\Kuliah\joki\radit\desa\backend\toolbox"
    # Atau gunakan "." untuk folder tempat script ini berada.
    target_directory = input("Masukkan path folder (tekan Enter untuk folder saat ini): ").strip()
    if not target_directory:
        target_directory = "."

    print("Sedang memproses folder dan file...")
    result = generate_llm_context(target_directory)

    # Menyimpan hasil ke file teks
    output_file = "konteks_llm.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"Selesai! Hasil telah disimpan di file: {output_file}")
    print(f"Silakan buka file '{output_file}' (misal di VS Code), lalu tekan Ctrl+A dan Ctrl+C untuk di-paste ke AI.")