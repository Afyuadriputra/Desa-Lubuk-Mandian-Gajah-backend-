# features/layanan_administrasi/tests/test_integration.py

import json
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestSuratEndToEnd:
    @patch("features.layanan_administrasi.services.SuratDocumentRenderer.render_docx")
    def test_should_complete_full_flow_from_template_to_download(
        self,
        mock_render_docx,
        client,
        uploaded_docx_file,
    ):
        mock_render_docx.return_value = b"FAKE-DOCX-CONTENT"

        admin = User.objects.create_superuser(
            nik="1111111111111111",
            password="password",
            nama_lengkap="Admin E2E",
            role="SUPERADMIN",
        )
        warga = User.objects.create_user(
            nik="2222222222222222",
            password="password",
            nama_lengkap="Warga E2E",
            role="WARGA",
        )

        # 1. Admin upload template surat
        client.force_login(admin)

        response = client.post(
            "/api/v1/layanan-administrasi/template-surat",
            data={
                "kode": "SKU",
                "nama": "Surat Keterangan Usaha",
                "deskripsi": "Template surat usaha.",
                "is_active": "true",
                "file_template": uploaded_docx_file,
            },
        )

        assert response.status_code == 201
        template_id = response.json()["id"]

        # 2. Warga melihat template aktif
        client.force_login(warga)

        response = client.get("/api/v1/layanan-administrasi/template-surat/aktif")

        assert response.status_code == 200
        assert any(item["id"] == template_id for item in response.json())

        # 3. Warga mengajukan surat dengan template_id
        payload_submit = {
            "template_id": template_id,
            "keperluan": "Pengajuan surat untuk membuka usaha warung.",
        }

        response = client.post(
            "/api/v1/layanan-administrasi/surat/ajukan",
            data=json.dumps(payload_submit),
            content_type="application/json",
        )

        assert response.status_code == 201
        surat_id = str(response.json()["id"])

        # 4. Admin memproses sesuai state machine
        client.force_login(admin)

        def proses(status, **extra_data):
            payload = {"status": status}
            payload.update(extra_data)
            return client.post(
                f"/api/v1/layanan-administrasi/surat/{surat_id}/proses",
                data=json.dumps(payload),
                content_type="application/json",
            )

        response = proses("VERIFIED")
        assert response.status_code == 200

        response = proses("PROCESSED", nomor_surat="001/SKU/IV/2026")
        assert response.status_code == 200

        response = proses("DONE")
        assert response.status_code == 200
        assert response.json()["docx_url"] is not None

        # 5. Warga download hasil surat
        client.force_login(warga)

        response = client.get(f"/api/v1/layanan-administrasi/surat/{surat_id}/download")

        assert response.status_code == 200
        mock_render_docx.assert_called_once()