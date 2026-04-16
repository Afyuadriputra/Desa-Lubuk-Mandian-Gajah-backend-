import os

def generate_context():
    # Nama file output
    output_file = "tests_layanan_context.txt"
    
    # Daftar abaikan
    ignore_dirs = {'__pycache__', 'logs'}
    ignore_files = {output_file, 'generate_tests_layanan_context.py'}
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    with open(output_file, 'w', encoding='utf-8') as f_out:
        f_out.write("CONTEXT: UNIT & INTEGRATION TESTS - LAYANAN ADMINISTRASI\n")
        f_out.write(f"Location: {current_dir}\n")
        f_out.write("="*70 + "\n\n")

        # Mengambil daftar file secara urut agar rapi
        files = [f for f in os.listdir(current_dir) if os.path.isfile(os.path.join(current_dir, f))]
        files.sort()

        for file in files:
            if file in ignore_files:
                continue
            
            file_path = os.path.join(current_dir, file)
            
            # Header untuk setiap file
            f_out.write(f" FILE: {file} ".center(70, "#") + "\n")
            
            try:
                # Cek ukuran file
                if os.path.getsize(file_path) == 0:
                    f_out.write("\n[ INFO: File ini kosong ]\n")
                else:
                    with open(file_path, 'r', encoding='utf-8') as f_in:
                        content = f_in.read()
                        f_out.write("\n" + content.strip() + "\n")
            except Exception as e:
                f_out.write(f"\n[ Error membaca file: {e} ]\n")
            
            f_out.write("\n" + "="*70 + "\n\n")

    print(f"✅ Berhasil! File konteks dibuat: {output_file}")

if __name__ == "__main__":
    generate_context()