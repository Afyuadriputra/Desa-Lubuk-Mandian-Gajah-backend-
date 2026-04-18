import os

def generate_llm_context_per_feature(base_path, target_dirs):
    """
    Mengambil isi file dari folder target dan merangkumnya ke dalam 
    file Markdown terpisah untuk setiap fitur.
    """
    for target_dir in target_dirs:
        # Mengambil nama fitur dari teks target_dir (misal: "profil_wilayah")
        feature_name = target_dir.split('/')[0]
        output_file = f"llm_context_{feature_name}_tests.md"
        
        # Normalkan path agar kompatibel dengan sistem operasi Windows/Linux
        full_target_dir = os.path.join(base_path, os.path.normpath(target_dir))
        
        if not os.path.exists(full_target_dir):
            print(f"⚠️ Folder tidak ditemukan, dilewati: {full_target_dir}")
            continue
            
        with open(output_file, 'w', encoding='utf-8') as out_f:
            out_f.write(f"# LLM Context: Tests untuk fitur `{feature_name}`\n\n")
            out_f.write(f"Dokumen ini berisi kumpulan kode dari direktori `{target_dir}` untuk keperluan konteks LLM.\n\n")
            
            # Walk melalui folder dan subfolder
            for root, dirs, files in os.walk(full_target_dir):
                # Abaikan direktori __pycache__
                if '__pycache__' in dirs:
                    dirs.remove('__pycache__')
                    
                for file in files:
                    # Abaikan file terkompilasi (.pyc)
                    if file.endswith('.pyc'):
                        continue
                        
                    file_path = os.path.join(root, file)
                    # Mendapatkan path relatif untuk judul file
                    relative_path = os.path.relpath(file_path, base_path)
                    # Ganti backslash dengan slash untuk format Markdown
                    relative_path_md = relative_path.replace('\\', '/')
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as in_f:
                            content = in_f.read()
                        
                        # Menentukan syntax highlighting
                        ext = file.split('.')[-1]
                        lang = 'python' if ext == 'py' else ('text' if ext == 'txt' else ext)
                        
                        # Tulis ke file output
                        out_f.write(f"---\n## File: `{relative_path_md}`\n\n")
                        out_f.write(f"```{lang}\n")
                        out_f.write(content)
                        out_f.write(f"\n```\n\n")
                        
                        print(f"✅ Memproses: {relative_path_md} -> dimasukkan ke {output_file}")
                        
                    except Exception as e:
                        print(f"❌ Gagal membaca {file_path}: {e}")
        
        print(f"📄 Selesai! File berhasil dibuat: {output_file}\n")

if __name__ == "__main__":
    # Direktori tempat script dijalankan (di dalam folder 'features')
    BASE_DIR = "."  
    
    # Target folder yang diminta
    TARGET_DIRS = [
        "profil_wilayah/tests",
        "publikasi_informasi/tests",
        "potensi_ekonomi/tests",
        "layanan_administrasi/tests"
    ]
    
    print("Memulai proses pembuatan konteks LLM...\n")
    generate_llm_context_per_feature(BASE_DIR, TARGET_DIRS)
    print("🎉 Seluruh proses selesai!")