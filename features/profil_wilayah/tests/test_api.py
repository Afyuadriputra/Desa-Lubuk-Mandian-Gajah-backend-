import json

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from features.profil_wilayah.models import ProfilDesa, WilayahDusun, WilayahPerangkat


@pytest.mark.django_db
class TestProfilWilayahAPI:
    def test_publik_bisa_akses_tanpa_login_dan_teragregasi(self, client, django_user_model):
        ProfilDesa.objects.create(id=1, visi="Visi API", misi="Misi API", sejarah="Sejarah API")
        user = django_user_model.objects.create(
            nik="1234567890123456",
            nama_lengkap="Pak Sekdes",
        )
        WilayahPerangkat.objects.create(user=user, jabatan="Sekdes", is_published=True)

        response = client.get("/api/v1/profil-wilayah/publik")

        assert response.status_code == 200
        data = response.json()
        assert "profil" in data
        assert "perangkat" in data
        assert data["profil"]["visi"] == "Visi API"
        assert data["perangkat"][0]["nama"] == "Pak Sekdes"
        assert data["perangkat"][0]["jabatan"] == "Sekdes"

    def test_update_profil_dengan_xss_otomatis_bersih(self, client, admin_user):
        client.force_login(admin_user)
        payload = {
            "visi": "<b>Visi Hebat</b>",
            "misi": "Misi Kuat",
            "sejarah": "<script>console.log('xss')</script> Sejarah lama",
        }

        response = client.put(
            "/api/v1/profil-wilayah/admin/profil",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert "<b>Visi Hebat</b>" in data["visi"]
        assert "<script>" not in data["sejarah"]
        assert "Sejarah lama" in data["sejarah"]

    def test_admin_bisa_tambah_dusun(self, client, admin_user):
        client.force_login(admin_user)

        response = client.post(
            "/api/v1/profil-wilayah/admin/dusun",
            data=json.dumps({
                "nama_dusun": "Mawar",
                "kepala_dusun": "Pak Budi",
            }),
            content_type="application/json",
        )

        assert response.status_code == 201
        assert WilayahDusun.objects.count() == 1

    def test_admin_bisa_update_dusun(self, client, admin_user):
        client.force_login(admin_user)
        dusun = WilayahDusun.objects.create(
            nama_dusun="Mawar",
            kepala_dusun="Pak Budi",
        )

        response = client.put(
            f"/api/v1/profil-wilayah/admin/dusun/{dusun.id}",
            data=json.dumps({
                "nama_dusun": "Melati",
                "kepala_dusun": "Pak Joko",
            }),
            content_type="application/json",
            follow=True,
        )

        assert response.status_code == 200, response.content.decode()
        dusun.refresh_from_db()
        assert dusun.nama_dusun == "Melati"
        assert dusun.kepala_dusun == "Pak Joko"

    def test_admin_bisa_hapus_dusun(self, client, admin_user):
        client.force_login(admin_user)
        dusun = WilayahDusun.objects.create(
            nama_dusun="Mawar",
            kepala_dusun="Pak Budi",
        )

        response = client.delete(
            f"/api/v1/profil-wilayah/admin/dusun/{dusun.id}",
            follow=True,
        )

        assert response.status_code == 200, response.content.decode()
        assert WilayahDusun.objects.count() == 0

    def test_admin_bisa_tambah_perangkat(self, client, admin_user, django_user_model):
        client.force_login(admin_user)
        user = django_user_model.objects.create(
            nik="1234567890123456",
            nama_lengkap="Ibu Kasi",
        )
        foto = SimpleUploadedFile(
            "foto.jpg",
            b"fake-image-content",
            content_type="image/jpeg",
        )

        response = client.post(
            "/api/v1/profil-wilayah/admin/perangkat",
            data={
                "user_id": str(user.id),
                "jabatan": "Kasi",
                "is_published": "true",
                "foto": foto,
            },
        )

        assert response.status_code == 201
        assert WilayahPerangkat.objects.count() == 1

    def test_admin_bisa_update_perangkat(self, client, admin_user, django_user_model):
        client.force_login(admin_user)
        user = django_user_model.objects.create(
            nik="1234567890123457",
            nama_lengkap="Pak Lama",
        )
        perangkat = WilayahPerangkat.objects.create(
            user=user,
            jabatan="Kaur",
            is_published=False,
        )

        response = client.put(
            f"/api/v1/profil-wilayah/admin/perangkat/{perangkat.id}",
            data=json.dumps({
                "user_id": str(user.id),
                "jabatan": "Sekdes",
                "is_published": True,
            }),
            content_type="application/json",
            follow=True,
        )

        assert response.status_code == 200, response.content.decode()
        perangkat.refresh_from_db()
        assert perangkat.jabatan == "Sekdes"
        assert perangkat.is_published is True

    def test_admin_bisa_hapus_perangkat(self, client, admin_user, django_user_model):
        client.force_login(admin_user)
        user = django_user_model.objects.create(
            nik="1234567890123458",
            nama_lengkap="Pak Hapus",
        )
        perangkat = WilayahPerangkat.objects.create(
            user=user,
            jabatan="Kaur",
            is_published=False,
        )

        response = client.delete(
            f"/api/v1/profil-wilayah/admin/perangkat/{perangkat.id}",
            follow=True,
        )

        assert response.status_code == 200, response.content.decode()
        assert WilayahPerangkat.objects.count() == 0