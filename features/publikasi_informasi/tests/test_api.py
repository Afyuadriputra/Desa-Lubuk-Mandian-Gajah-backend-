# features/publikasi_informasi/tests/test_api.py
import pytest
import json
from django.urls import reverse
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

    def test_named_route_detail_draft_tersembunyi_dari_publik(self, client, admin_user):
        client.force_login(admin_user)
        draft = Publikasi.objects.create(
            judul="Draft Rahasia",
            slug="draft-rahasia",
            konten_html="<p>Rahasia</p>",
            jenis="BERITA",
            status="DRAFT",
            penulis=admin_user,
        )

        client.logout()
        response = client.get(reverse("publikasi-detail", kwargs={"slug": draft.slug}))

        assert response.status_code == 404

    def test_admin_bisa_update_dan_delete_publikasi(self, client, admin_user):
        client.force_login(admin_user)
        publikasi = Publikasi.objects.create(
            judul="Berita Lama",
            slug="berita-lama",
            konten_html="<p>Lama</p>",
            jenis="BERITA",
            status="DRAFT",
            penulis=admin_user,
        )

        update_response = client.put(
            reverse("publikasi-admin-update", kwargs={"slug": publikasi.slug}),
            data=json.dumps(
                {
                    "judul": "Berita Baru",
                    "konten_html": "<p>Konten baru</p>",
                    "jenis": "BERITA",
                    "status": "PUBLISHED",
                }
            ),
            content_type="application/json",
        )

        assert update_response.status_code == 200
        publikasi.refresh_from_db()
        assert publikasi.judul == "Berita Baru"
        assert publikasi.status == "PUBLISHED"

        delete_response = client.delete(reverse("publikasi-admin-delete", kwargs={"slug": publikasi.slug}))
        assert delete_response.status_code == 200
        assert Publikasi.objects.filter(id=publikasi.id).exists() is False

    def test_admin_bisa_list_publikasi_changelist(self, client, admin_user):
        client.force_login(admin_user)
        Publikasi.objects.create(
            judul="Berita Admin",
            slug="berita-admin",
            konten_html="<p>Admin</p>",
            jenis="BERITA",
            status="DRAFT",
            penulis=admin_user,
        )

        response = client.get(reverse("publikasi-admin-list"))

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["judul"] == "Berita Admin"
