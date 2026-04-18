import pytest
import json
from django.core.files.uploadedfile import SimpleUploadedFile  # <-- Dipindah ke atas
from features.pengaduan_warga.models import LayananPengaduan

@pytest.mark.django_db
class TestPengaduanAPI:

    def test_buat_pengaduan_dengan_form_data(self, client, warga_user):
        """KISS: Menguji Form-Data di Ninja API"""
        client.force_login(warga_user)
        
        # Tidak pakai json.dumps karena ini Form-Data
        payload = {
            "kategori": "Infrastruktur",
            "judul": "Jalan Berlubang",
            "deskripsi": "Jalan di RT 02 berlubang parah"
        }
        response = client.post("/api/v1/pengaduan/buat", data=payload)
        
        assert response.status_code == 201
        assert response.json()["status"] == "OPEN"

    def test_list_pengaduan_yagni_tanpa_histori(self, client, warga_user):
        """YAGNI: Memastikan list tidak memuat histori yang berat."""
        client.force_login(warga_user)
        LayananPengaduan.objects.create(pelapor=warga_user, kategori="Keamanan", judul="Maling", deskripsi="Ada maling ayam")
        
        response = client.get("/api/v1/pengaduan/")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 1
        assert "histori" not in data[0] # Pastikan struktur ringkas
        assert "deskripsi" not in data[0] # YAGNI: List hanya butuh judul & status
    
    def test_upload_file_bukan_gambar_ditolak(self, client, warga_user):
        client.force_login(warga_user)
        bad_file = SimpleUploadedFile("script_jahat.txt", b"print('hack')", content_type="text/plain")
        payload = {
            "kategori": "Keamanan",
            "judul": "Test Upload",
            "deskripsi": "Ini adalah deskripsi yang panjang agar lolos validasi", # PERBAIKAN DI SINI
            "foto_bukti": bad_file
        }
        response = client.post("/api/v1/pengaduan/buat", data=payload)
        assert response.status_code == 400
        assert "format file" in response.json().get("detail", "").lower() or "gambar" in response.json().get("detail", "").lower()

    def test_upload_file_terlalu_besar_ditolak(self, client, warga_user):
        client.force_login(warga_user)
        huge_file = SimpleUploadedFile("huge.jpg", b"0" * ((5 * 1024 * 1024) + 1), content_type="image/jpeg")
        payload = {
            "kategori": "Infrastruktur",
            "judul": "Test Upload",
            "deskripsi": "Ini adalah deskripsi yang panjang agar lolos validasi", # PERBAIKAN DI SINI
            "foto_bukti": huge_file
        }
        response = client.post("/api/v1/pengaduan/buat", data=payload)
        assert response.status_code == 400
        assert "maksimal" in response.json().get("detail", "").lower()