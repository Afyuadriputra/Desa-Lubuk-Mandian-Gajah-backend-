import os
import frontmatter
from pathlib import Path

def sync_obsidian_context(
    source_backend=".", 
    vault_brain_path="../Obsidian/brain"
):
    backend_path = Path(source_backend).resolve()
    vault_path = Path(vault_brain_path).resolve()
    arch_path = vault_path / "arsitektur"
    
    # Pastikan folder arsitektur ada
    arch_path.mkdir(parents=True, exist_ok=True)

    # Mapping PRD ke Folder Feature
    mapping = {
        "01 - Backend Architecture.md": "core_django",
        "02 - Modul Auth Warga.md": "auth_warga",
        "03 - Modul Profil Wilayah.md": "profil_wilayah",
        "04 - Modul Publikasi Informasi.md": "publikasi_informasi",
        "05 - Modul Potensi Ekonomi.md": "potensi_ekonomi",
        "06 - Modul Layanan Administrasi.md": "layanan_administrasi",
        "07 - Modul Pengaduan Warga.md": "pengaduan_warga"
    }

    print(f"🔄 Memulai sinkronisasi arsitektur ke: {vault_path}")

    for prd_filename, feature_dirname in mapping.items():
        prd_file_path = vault_path / prd_filename
        arch_node_path = arch_path / f"{feature_dirname}.md"

        # 1. Update PRD Lama (Hanya bagian Properties/Frontmatter)
        if prd_file_path.exists():
            post = frontmatter.load(prd_file_path)
            # Menambahkan link ke arsitektur tanpa merubah body teks
            post['architecture_node'] = f"[[{feature_dirname}]]"
            post['status'] = "linked_to_code"
            
            with open(prd_file_path, 'wb') as f:
                frontmatter.dump(post, f)
            print(f"✅ Metadata PRD diupdate: {prd_filename}")

        # 2. Buat/Update Node Arsitektur Baru
        # Mencari file .py di folder terkait untuk daftar komponen
        feature_path = backend_path / "features" / feature_dirname
        if not feature_path.exists(): # Jika core_django
            feature_path = backend_path / feature_dirname

        py_files = []
        if feature_path.exists():
            py_files = [f.name for f in feature_path.glob("*.py") if f.name != "__init__.py"]

        # Buat konten Node Arsitektur
        arch_content = f"# Arsitektur: {feature_dirname}\n\n"
        arch_content += f"**Dokumen Terkait:** [[{prd_filename}|PRD Rencana]]\n\n"
        arch_content += "### Komponen Clean Architecture\n"
        for py_file in sorted(py_files):
            arch_content += f"- [[{feature_dirname}_{py_file}|{py_file}]]\n"

        # Gunakan frontmatter untuk node arsitektur juga agar rapi
        arch_post = frontmatter.Post(arch_content)
        arch_post['type'] = "architecture_node"
        arch_post['feature'] = feature_dirname
        
        with open(arch_node_path, 'wb') as f:
            frontmatter.dump(arch_post, f)
        
        # 3. Buat file detail komponen (misal: auth_warga_services.py.md)
        for py_file in py_files:
            comp_path = arch_path / f"{feature_dirname}_{py_file}.md"
            if not comp_path.exists():
                with open(comp_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {py_file}\n\nModul: [[{feature_dirname}]]\nLayer: Clean Architecture")

    print("\n🚀 Sinkronisasi selesai. Silakan cek 'Properties' di Obsidian Anda.")

if __name__ == "__main__":
    sync_obsidian_context()