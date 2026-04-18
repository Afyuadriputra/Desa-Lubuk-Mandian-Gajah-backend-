import json
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestSuratEndToEnd:

    def test_should_complete_full_flow_from_submit_to_done(self, client):
        admin = User.objects.create_superuser(
            nik="1111111111111111", 
            password="password", 
            nama_lengkap="Admin E2E", 
            role="SUPERADMIN"
        )
        warga = User.objects.create_user(
            nik="2222222222222222", 
            password="password", 
            nama_lengkap="Warga E2E", 
            role="WARGA"
        )

        client.force_login(warga)
        payload_submit = {"jenis_surat": "SKU", "keperluan": "Pengajuan surat usaha"}
        response = client.post("/api/v1/layanan-administrasi/surat/ajukan", data=json.dumps(payload_submit), content_type="application/json")
        
        assert response.status_code == 201
        surat_id = str(response.json()["id"])

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