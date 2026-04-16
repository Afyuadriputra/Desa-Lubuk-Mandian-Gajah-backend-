import json
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
class TestSuratEndToEnd:

    def test_should_complete_full_flow_from_submit_to_done(self, client):
        """End-to-end: warga submit → admin proses → DONE"""

        # 🔹 SETUP USERS
        admin = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="Admin",
            role="ADMIN",
            is_staff=True,
        )

        warga = User.objects.create_user(
            nik="2222222222222222",
            password="password123",
            nama_lengkap="Warga",
            role="WARGA",
        )

        # =========================
        #  STEP 1: SUBMIT SURAT
        # =========================
        client.force_login(warga)

        payload_submit = {
            "jenis_surat": "SKU",
            "keperluan": "Pengajuan surat usaha untuk keperluan administrasi",
        }

        response = client.post(
            reverse("surat-ajukan"),
            data=json.dumps(payload_submit),
            content_type="application/json",
        )

        assert response.status_code == 201
        surat_id = response.json()["data"]["id"]

        # =========================
        #  STEP 2: ADMIN PROSES
        # =========================
        client.force_login(admin)

        def proses(status):
            return client.post(
                reverse("surat-proses", kwargs={"surat_id": surat_id}),
                data=json.dumps({"status": status}),
                content_type="application/json",
            )

        # VERIFIED
        response = proses("VERIFIED")
        assert response.status_code == 200

        # PROCESSED
        response = proses("PROCESSED")
        assert response.status_code == 200

        # DONE
        response = proses("DONE")
        assert response.status_code == 200

        # =========================
        #  ASSERT FINAL STATE
        # =========================
        assert response.json()["data"]["status"] == "DONE"