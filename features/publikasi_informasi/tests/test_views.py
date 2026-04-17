import json
import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

class TestPublikasiAPI:
    def test_list_publikasi_publik_mengembalikan_200(self, client, mocker):
        """KISS: Pastikan API publik berjalan normal tanpa autentikasi."""
        mock_publikasi = mocker.Mock(
            judul="Judul 1", slug="judul-1", jenis="BERITA", 
            penulis=mocker.Mock(nama_lengkap="Admin"), 
            published_at=None
        )
        mocker.patch("features.publikasi_informasi.views.publikasi_service.get_publikasi_publik", return_value=[mock_publikasi])

        url = reverse('publikasi-list-publik')
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.json()["data"]) == 1
        assert response.json()["data"][0]["judul"] == "Judul 1"

    def test_buat_publikasi_admin_ditolak_tanpa_login(self, client):
        url = reverse('publikasi-admin-buat')
        response = client.post(url, data={})
        
        assert response.status_code == 401

    def test_buat_publikasi_admin_berhasil_201(self, client, mocker):
        mocker.patch("features.publikasi_informasi.views.is_active_user", return_value=True)
        mocker.patch(
            "features.publikasi_informasi.views.publikasi_service.buat_publikasi", 
            return_value=mocker.Mock(slug="tes-berita")
        )

        url = reverse('publikasi-admin-buat')
        payload = {
            "judul": "Tes Berita",
            "konten_html": "<p>Panjang kontennya</p>",
            "jenis": "BERITA",
            "status": "DRAFT"
        }
        
        response = client.post(url, data=json.dumps(payload), content_type="application/json")

        assert response.status_code == 201
        assert response.json()["slug"] == "tes-berita"