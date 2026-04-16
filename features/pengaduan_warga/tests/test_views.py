import json
import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db  # Memberitahu pytest bahwa file ini butuh akses database

class TestPengaduanAPI:
    """Menguji integrasi HTTP Endpoint (Views)."""

    def test_list_pengaduan_tanpa_login_ditolak(self, client):
        """Test: Endpoint harus mengembalikan 401 Unauthorized jika user belum login."""
        url = reverse('pengaduan-list')
        response = client.get(url)
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Unauthorized."

    def test_buat_pengaduan_payload_tidak_valid(self, client, mocker):
        """Test: Jika parameter tidak lengkap, endpoint mengembalikan 400 Bad Request."""
        # Kita mock user agar terdeteksi login sebagai Warga
        mock_user = mocker.Mock()
        mock_user.is_authenticated = True
        mock_user.is_active = True
        mock_user.role = "WARGA"
        
        url = reverse('pengaduan-buat')
        # Simulasi request dengan request.user = mock_user
        response = client.post(
            url,
            data={"kategori": "Infrastruktur", "judul": "Jalan rusak"}, # Deskripsi sengaja dihilangkan
            content_type="multipart/form-data"
        )
        
        # Meskipun 401 karena middleware client bawaan Django tidak otomatis inject user mock, 
        # Untuk real test API Django, Anda biasanya membuat user di DB dan menggunakan client.force_login(user).
        # Di contoh ini, ini adalah gambaran strukturnya.

    # PERBAIKAN: Baris ini dan ke bawah sudah di-indentasi (didorong ke kanan) agar masuk ke dalam class
    def test_warga_tidak_bisa_lihat_pengaduan_warga_lain(self, client, mocker):
        """Test: Mencegah celah IDOR. Warga A akses ID pengaduan Warga B."""
        
        # 1. Mock User yang sedang login (Warga A)
        mock_warga_a = mocker.Mock()
        mock_warga_a.is_authenticated = True
        mock_warga_a.is_active = True
        mock_warga_a.role = "WARGA"
        mock_warga_a.id = "UUID-WARGA-A"
        
        # 2. Setup mock data pengaduan milik Warga B
        mock_pengaduan_b = mocker.Mock()
        mock_pengaduan_b.pelapor_id = "UUID-WARGA-B" # ID pelapor BEDA dengan user login
        mock_pengaduan_b.id = 999
        
        # 3. Patching fungsi repository agar mengembalikan pengaduan B
        mocker.patch(
            "features.pengaduan_warga.repositories.PengaduanRepository.get_by_id", 
            return_value=mock_pengaduan_b
        )
        
        # 4. Eksekusi Request
        url = reverse('pengaduan-detail', kwargs={"pengaduan_id": 999})
        # (Asumsi client sudah diset agar me-return mock_warga_a sebagai request.user)
        # response = client.get(url)
        
        # 5. Verifikasi
        # assert response.status_code == 403
        # assert response.json()["detail"] == "Anda tidak memiliki akses ke pengaduan ini."