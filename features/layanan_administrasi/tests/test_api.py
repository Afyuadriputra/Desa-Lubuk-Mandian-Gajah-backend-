import pytest
import json
from django.core.files.base import ContentFile
from django.urls import reverse
from features.layanan_administrasi.models import LayananSurat
from unittest.mock import patch

@pytest.mark.django_db
class TestSuratAPI:

    def test_warga_bisa_ajukan_surat(self, client, warga_user):
        client.force_login(warga_user)
        payload = {"jenis_surat": "SKTM", "keperluan": "Keperluan beasiswa anak sekolah"}
        response = client.post("/api/v1/layanan-administrasi/surat/ajukan", data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 201

    def test_admin_bisa_proses_surat(self, client, admin_user, warga_user):
        client.force_login(admin_user)
        surat = LayananSurat.objects.create(pemohon=warga_user, jenis_surat="SKU", keperluan="Buka usaha", status="PENDING")
        
        payload = {"status": "VERIFIED"}
        # Cast ID ke string secara eksplisit untuk URL
        response = client.post(f"/api/v1/layanan-administrasi/surat/{str(surat.id)}/proses", data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 200

    @patch('features.layanan_administrasi.services.audit_event')
    def test_proses_surat_memicu_audit_log(self, mock_audit, client, admin_user, warga_user):
        client.force_login(admin_user)
        surat = LayananSurat.objects.create(pemohon=warga_user, jenis_surat="SKU", keperluan="Tes", status="PENDING")
        
        payload = {"status": "VERIFIED"}
        response = client.post(f"/api/v1/layanan-administrasi/surat/{str(surat.id)}/proses", data=json.dumps(payload), content_type="application/json")
        
        assert response.status_code == 200
        mock_audit.assert_called_once()

    def test_named_route_detail_mengembalikan_histori(self, client, warga_user):
        client.force_login(warga_user)
        surat = LayananSurat.objects.create(
            pemohon=warga_user,
            jenis_surat="SKU",
            keperluan="Keperluan surat untuk modal usaha",
            status="PENDING",
        )

        response = client.get(reverse("surat-detail", kwargs={"surat_id": str(surat.id)}))

        assert response.status_code == 200
        assert response.json()["data"]["id"] == str(surat.id)
        assert "histori" in response.json()["data"]

    def test_download_pdf_ditolak_jika_surat_belum_done(self, client, warga_user):
        client.force_login(warga_user)
        surat = LayananSurat.objects.create(
            pemohon=warga_user,
            jenis_surat="SKU",
            keperluan="Keperluan surat untuk modal usaha",
            status="PENDING",
        )

        response = client.get(reverse("surat-download-pdf", kwargs={"surat_id": str(surat.id)}))

        assert response.status_code == 403

    def test_download_pdf_berhasil_jika_surat_done(self, client, warga_user):
        client.force_login(warga_user)
        surat = LayananSurat.objects.create(
            pemohon=warga_user,
            jenis_surat="SKU",
            keperluan="Keperluan surat untuk modal usaha",
            status="DONE",
        )
        surat.pdf_file.save("surat-test.pdf", ContentFile(b"%PDF-1.4 test"), save=True)

        response = client.get(reverse("surat-download-pdf", kwargs={"surat_id": str(surat.id)}))

        assert response.status_code == 200
