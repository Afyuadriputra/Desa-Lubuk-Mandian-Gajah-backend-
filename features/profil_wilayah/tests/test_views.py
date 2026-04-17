import json
import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

class TestProfilWilayahAPI:
    def test_profil_publik_bisa_diakses_tanpa_login(self, client, mocker):
        """KISS: Sesuai MVP, data publik harus terbuka."""
        # Mock responses from services
        mock_profil = mocker.Mock(visi="Visi 1", misi="Misi 1", sejarah="Sejarah 1")
        mocker.patch("features.profil_wilayah.views.profil_service.get_profil", return_value=mock_profil)
        mocker.patch("features.profil_wilayah.views.perangkat_service.get_perangkat_publik", return_value=[])

        url = reverse('profil-publik')
        response = client.get(url)

        assert response.status_code == 200
        assert response.json()["profil"]["visi"] == "Visi 1"

    def test_tambah_dusun_harus_401_jika_belum_login(self, client):
        url = reverse('admin-dusun-tambah')
        response = client.post(url, data={})
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Unauthorized"

    def test_tambah_dusun_harus_201_jika_sukses(self, client, mocker):
        mocker.patch("features.profil_wilayah.views.is_active_user", return_value=True)
        mocker.patch("features.profil_wilayah.views.dusun_service.tambah_dusun", return_value=mocker.Mock(id=5))

        url = reverse('admin-dusun-tambah')
        payload = {"nama_dusun": "Melati", "kepala_dusun": "Siti"}
        
        response = client.post(url, data=json.dumps(payload), content_type="application/json")

        assert response.status_code == 201
        assert response.json()["id"] == 5

    def test_tambah_perangkat_menangani_exception_dengan_400(self, client, mocker):
        mocker.patch("features.profil_wilayah.views.is_active_user", return_value=True)
        # Simulasi jika layer service melemparkan exception (misal: validasi gagal)
        mocker.patch(
            "features.profil_wilayah.views.perangkat_service.tambah_perangkat", 
            side_effect=Exception("Jabatan wajib diisi")
        )

        url = reverse('admin-perangkat-tambah')
        response = client.post(url, data={"jabatan": ""})

        assert response.status_code == 400
        assert "wajib diisi" in response.json()["detail"]