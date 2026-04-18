# features/publikasi_informasi/tests/test_api.py
import pytest
import json
from features.publikasi_informasi.models import Publikasi

@pytest.mark.django_db
class TestPublikasiAPI:

    def test_buat_publikasi_otomatis_slug_dan_sanitasi(self, client, admin_user):
        client.force_login(admin_user)
        payload = {
            "judul": "Pengumuman Desa",
            "konten_html": "<h1>Info</h1><script>alert(1)</script>",
            "jenis": "PENGUMUMAN",
            "status": "DRAFT"
        }
        response = client.post("/api/v1/publikasi/admin/buat", data=json.dumps(payload), content_type="application/json")
        
        assert response.status_code == 201
        data = response.json()
        assert "pengumuman-desa" in data["slug"]
        assert "<script>" not in data["konten_html"]

    def test_publikasi_list_tidak_mengirim_html_panjang(self, client):
        Publikasi.objects.create(judul="Berita 1", slug="berita-1", konten_html="<p>Isi panjang</p>", status="PUBLISHED")
        response = client.get("/api/v1/publikasi/publik")
        
        assert response.status_code == 200
        data = response.json()
        assert "konten_html" not in data[0]