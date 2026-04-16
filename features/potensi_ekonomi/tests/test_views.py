import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

class TestPotensiEkonomiAPI:
    def test_katalog_publik_ditolak_tanpa_login(self, client):
        url = reverse('ekonomi-katalog')
        response = client.get(url)
        assert response.status_code == 401

    def test_admin_bisa_akses_list_admin(self, client, mocker):
        mock_admin = mocker.Mock()
        mock_admin.is_authenticated = True
        mock_admin.is_active = True
        mock_admin.role = "BUMDES"
        
        # Memaksa permission untuk test ini agar merespon admin valid
        mocker.patch("features.potensi_ekonomi.views.is_active_user", return_value=True)
        mocker.patch("features.potensi_ekonomi.services.PotensiEkonomiService.get_semua_unit_admin", return_value=[])

        url = reverse('ekonomi-admin-list')
        response = client.get(url)
        
        assert response.status_code == 200

    def test_buat_unit_gagal_jika_kategori_invalid(self, client, mocker):
        # Simulasi Admin login
        mocker.patch("features.potensi_ekonomi.views.is_active_user", return_value=True)
        
        # PERBAIKAN: Ubah target mock ke services.py
        mocker.patch("features.potensi_ekonomi.services.can_manage_data_bumdes", return_value=True)
        
        url = reverse('ekonomi-admin-buat')
        response = client.post(
            url,
            data={"nama_usaha": "Wisata Alam", "kategori": "KATEGORI_ASAL"}
        )
        
        # Harus tertangkap oleh blok exc PotensiEkonomiError (status 400)
        assert response.status_code == 400
        assert "tidak valid" in response.json()["detail"]