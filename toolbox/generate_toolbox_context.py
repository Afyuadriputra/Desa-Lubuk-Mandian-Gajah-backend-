import os

def generate_toolbox_context(output_file="toolbox_context.txt"):
    # Daftar folder dan file yang diabaikan
    ignore_dirs = {'__pycache__', '.git', 'env', '.venv'}
    ignore_files = {'__init__.py', 'generate_toolbox_context.py', output_file, 'semua_kode_toolbox.txt'}
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    with open(output_file, 'w', encoding='utf-8') as f_out:
        f_out.write("SYSTEM TOOLBOX CONTEXT - SHARED UTILITIES\n")
        f_out.write(f"Root: {current_dir}\n")
        f_out.write("="*70 + "\n\n")

        for root, dirs, files in os.walk(current_dir):
            # Filter direktori yang diabaikan secara in-place
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                if file in ignore_files:
                    continue
                
                # Mendapatkan path relatif untuk identifikasi sub-modul (misal: logging/audit.py)
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, current_dir)
                
                # Header file dengan path lengkap
                f_out.write(f" MODULE: {relative_path} ".center(70, "#") + "\n")
                
                try:
                    # Cek jika file benar-benar kosong
                    if os.path.getsize(file_path) == 0:
                        f_out.write("\n[ KETERANGAN: File ini kosong (0 bytes) ]\n")
                    else:
                        with open(file_path, 'r', encoding='utf-8') as f_in:
                            content = f_in.read().strip()
                            if not content:
                                f_out.write("\n[ KETERANGAN: File hanya berisi whitespace ]\n")
                            else:
                                f_out.write(content + "\n")
                except Exception as e:
                    f_out.write(f"[ Error saat membaca file: {e} ]\n")
                
                f_out.write("\n" + "="*70 + "\n\n")

    print(f"Selesai! Konteks toolbox disimpan di: {output_file}")

if __name__ == "__main__":
    generate_toolbox_context()