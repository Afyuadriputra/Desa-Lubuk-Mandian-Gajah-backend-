import os

def build_feature_context(feature_path, target_files, output_name):
    """
    Mengambil file spesifik dari sebuah fitur untuk konteks LLM.
    """
    # Pastikan path menggunakan format yang benar untuk OS (Windows/Linux)
    feature_dir = os.path.normpath(feature_path)
    feature_name = os.path.basename(feature_dir)
    
    if not os.path.exists(feature_dir):
        print(f"❌ Error: Folder {feature_dir} tidak ditemukan.")
        return

    print(f"📂 Memproses Fitur: {feature_name}")
    
    with open(output_name, "w", encoding="utf-8") as out_f:
        out_f.write(f"# Context LLM: Fitur {feature_name}\n")
        out_f.write(f"Lokasi: `{feature_path}`\n\n")
        
        for file_name in target_files:
            file_path = os.path.join(feature_dir, file_name)
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as in_f:
                        content = in_f.read()
                    
                    # Menulis ke Markdown
                    out_f.write(f"---\n## File: `{feature_name}/{file_name}`\n\n")
                    out_f.write(f"```python\n")
                    out_f.write(content)
                    out_f.write(f"\n```\n\n")
                    print(f"✅ Berhasil mengambil: {file_name}")
                    
                except Exception as e:
                    print(f"⚠️ Gagal membaca {file_name}: {e}")
            else:
                # Karena kamu bilang "kalau ada", kita buat log saja jika tidak ada
                print(f"ℹ️ Skip: {file_name} (Tidak ditemukan)")

if __name__ == "__main__":
    # Path folder fitur
    PROFIL_PATH = "profil_wilayah" 
    
    # List file yang kamu minta
    FILES_TO_GET = [
        "api.py",
        "services.py",
        "repositories.py",
        "models.py",
        "permissions.py",
        "urls.py",
        "schemas.py" # Tambahan jika diperlukan karena biasanya ada di Ninja/FastAPI
    ]
    
    OUTPUT_FILE = "context_profil_wilayah.md"
    
    build_feature_context(PROFIL_PATH, FILES_TO_GET, OUTPUT_FILE)
    print(f"\n✨ Selesai! Konteks disimpan di: {OUTPUT_FILE}")