# features/layanan_administrasi/tests/test_api.py

import json
from unittest.mock import patch

import pytest
from django.core.files.base import ContentFile
from django.urls import reverse

from features.layanan_administrasi.models import LayananSurat


@pytest.mark.django_db
class TestTemplateSuratAPI:
    def test_admin_bisa_upload_template_surat(self, client, admin_user, uploaded_docx_file):
        client.force_login(admin_user)

        response = client.post(
            "/api/v1/layanan-administrasi/template-surat",
            data={
                "kode": "DOMISILI",
                "nama": "Surat Keterangan Domisili",
                "deskripsi": "Template domisili.",
                "is_active": "true",
                "file_template": uploaded_docx_file,
            },
        )

        assert response.status_code == 201
        assert response.json()["kode"] == "DOMISILI"

    def test_warga_tidak_bisa_upload_template_surat(self, client, warga_user, uploaded_docx_file):
        client.force_login(warga_user)

        response = client.post(
            "/api/v1/layanan-administrasi/template-surat",
            data={
                "kode": "DOMISILI",
                "nama": "Surat Keterangan Domisili",
                "file_template": uploaded_docx_file,
            },
        )

        assert response.status_code in [401, 403]

    def test_user_aktif_bisa_melihat_template_aktif(self, client, warga_user, template_surat_aktif):
        client.force_login(warga_user)

        response = client.get("/api/v1/layanan-administrasi/template-surat/aktif")

        assert response.status_code == 200
        assert len(response.json()) >= 1
        assert response.json()[0]["is_active"] is True

    def test_admin_bisa_melihat_semua_template(self, client, admin_user, template_surat_aktif, template_surat_nonaktif):
        client.force_login(admin_user)

        response = client.get("/api/v1/layanan-administrasi/template-surat")

        assert response.status_code == 200
        assert len(response.json()) >= 2


@pytest.mark.django_db
class TestSuratAPI:
    def test_warga_bisa_ajukan_surat_dengan_template_id(self, client, warga_user, template_surat_aktif):
        client.force_login(warga_user)

        payload = {
            "template_id": template_surat_aktif.id,
            "keperluan": "Keperluan beasiswa anak sekolah.",
        }

        response = client.post(
            "/api/v1/layanan-administrasi/surat/ajukan",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 201
        assert response.json()["template_id"] == template_surat_aktif.id
        assert response.json()["jenis_surat"] == template_surat_aktif.kode

    def test_legacy_warga_masih_bisa_ajukan_surat_dengan_jenis_surat(self, client, warga_user):
        client.force_login(warga_user)

        payload = {
            "jenis_surat": "SKTM",
            "keperluan": "Keperluan beasiswa anak sekolah.",
        }

        response = client.post(
            "/api/v1/layanan-administrasi/surat/ajukan",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 201
        assert response.json()["jenis_surat"] == "SKTM"

    def test_admin_bisa_proses_surat(self, client, admin_user, warga_user, template_surat_aktif):
        client.force_login(admin_user)

        surat = LayananSurat.objects.create(
            pemohon=warga_user,
            template=template_surat_aktif,
            jenis_surat=template_surat_aktif.kode,
            keperluan="Keperluan usaha warga.",
            status="PENDING",
        )

        payload = {"status": "VERIFIED"}

        response = client.post(
            f"/api/v1/layanan-administrasi/surat/{str(surat.id)}/proses",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert response.json()["status"] == "VERIFIED"

    @patch("features.layanan_administrasi.services.audit_event")
    def test_proses_surat_memicu_audit_log(self, mock_audit, client, admin_user, warga_user):
        client.force_login(admin_user)

        surat = LayananSurat.objects.create(
            pemohon=warga_user,
            jenis_surat="SKU",
            keperluan="Keperluan usaha warga.",
            status="PENDING",
        )

        payload = {"status": "VERIFIED"}

        response = client.post(
            f"/api/v1/layanan-administrasi/surat/{str(surat.id)}/proses",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 200
        mock_audit.assert_called_once()

    def test_named_route_detail_mengembalikan_histori(self, client, warga_user):
        client.force_login(warga_user)

        surat = LayananSurat.objects.create(
            pemohon=warga_user,
            jenis_surat="SKU",
            keperluan="Keperluan surat untuk modal usaha.",
            status="PENDING",
        )

        response = client.get(reverse("surat-detail", kwargs={"surat_id": str(surat.id)}))

        assert response.status_code == 200
        assert response.json()["data"]["id"] == str(surat.id)
        assert "histori" in response.json()["data"]

    def test_download_ditolak_jika_surat_belum_done(self, client, warga_user):
        client.force_login(warga_user)

        surat = LayananSurat.objects.create(
            pemohon=warga_user,
            jenis_surat="SKU",
            keperluan="Keperluan surat untuk modal usaha.",
            status="PENDING",
        )

        response = client.get(f"/api/v1/layanan-administrasi/surat/{str(surat.id)}/download")

        assert response.status_code == 403

    def test_download_docx_berhasil_jika_surat_done(self, client, warga_user):
        client.force_login(warga_user)

        surat = LayananSurat.objects.create(
            pemohon=warga_user,
            jenis_surat="SKU",
            keperluan="Keperluan surat untuk modal usaha.",
            status="DONE",
        )
        surat.docx_file.save("surat-test.docx", ContentFile(b"DOCX"), save=True)

        response = client.get(f"/api/v1/layanan-administrasi/surat/{str(surat.id)}/download")

        assert response.status_code == 200

    def test_download_fallback_pdf_jika_docx_tidak_ada(self, client, warga_user):
        client.force_login(warga_user)

        surat = LayananSurat.objects.create(
            pemohon=warga_user,
            jenis_surat="SKU",
            keperluan="Keperluan surat untuk modal usaha.",
            status="DONE",
        )
        surat.pdf_file.save("surat-test.pdf", ContentFile(b"%PDF-1.4 test"), save=True)

        response = client.get(f"/api/v1/layanan-administrasi/surat/{str(surat.id)}/download")

        assert response.status_code == 200