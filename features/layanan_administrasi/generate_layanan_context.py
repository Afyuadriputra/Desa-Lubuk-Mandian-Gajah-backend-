import os

def generate_context_with_empty_notif(output_file="layanan_context.txt"):
    # Daftar yang diabaikan agar LLM fokus pada logika
    ignore_dirs = {'__pycache__', 'migrations', 'tests', 'env', '.venv'}
    ignore_files = {'__init__.py', 'generate_layanan_context.py', output_file}
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    with open(output_file, 'w', encoding='utf-8') as f_out:
        f_out.write("CONTEXT: LAYANAN ADMINISTRASI FEATURE\n")
        f_out.write(f"Root: {current_dir}\n")
        f_out.write("="*60 + "\n\n")

        # Mengambil semua file di root folder ini
        for file in os.listdir(current_dir):
            file_path = os.path.join(current_dir, file)
            
            # Lewati jika folder atau file dalam daftar ignore
            if os.path.isdir(file_path) or file in ignore_files:
                continue

            # Header File
            f_out.write(f" FILE: {file} ".center(60, "=") + "\n")
            
            try:
                if os.path.getsize(file_path) == 0:
                    f_out.write("\n[ NOTIFIKASI: FILE INI KOSONG / BELUM ADA LOGIKA ]\n")
                else:
                    with open(file_path, 'r', encoding='utf-8') as f_in:
                        content = f_in.read().strip()
                        if not content:
                            f_out.write("\n[ NOTIFIKASI: FILE INI HANYA BERISI WHITESPACE/KOSONG ]\n")
                        else:
                            f_out.write(content + "\n")
            except Exception as e:
                f_out.write(f"[ Error membaca file: {e} ]\n")
            
            f_out.write("\n" + "-"*60 + "\n\n")

    print(f"Konteks berhasil dibuat: {output_file}")

if __name__ == "__main__":
    generate_context_with_empty_notif()