# tests/test_user_flows.py

import json
import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

from features.publikasi_informasi.services import PublikasiService

User = get_user_model()


@pytest.fixture
def warga():
    return User.objects.create_user(
        nik="3333333333333333",
        password="password123",
        nama_lengkap="Budi Warga",
        role="WARGA",
    )


@pytest.fixture
def admin():
    return User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="Pak Admin",
        role="ADMIN",
        is_staff=True,
    )


@pytest.fixture
def warga_client(warga):
    client = Client()
    client.force_login(warga)
    return client


@pytest.fixture
def admin_client(admin):
    client = Client()
    client.force_login(admin)
    return client


@pytest.mark.django_db
class TestUserFlows:

    # =====================================================================
    # 8.1 Flow Pengajuan Surat oleh Warga
    # =====================================================================
    @patch("features.layanan_administrasi.services.generate_pdf_from_html")
    @patch("features.layanan_administrasi.services.render_surat_html")
    def test_flow_pengajuan_surat(self, mock_render, mock_pdf, warga_client, admin_client):
        """Menguji Flow 8.1: Warga ajukan surat -> Admin proses sampai DONE -> Warga unduh PDF"""
        
        # Mocking WeasyPrint agar tidak perlu merender PDF beneran saat test
        mock_render.return_value = "<html>Mock HTML</html>"
        mock_pdf.return_value = b"Mock PDF Bytes"

        # 1 & 2 & 3 & 4 & 5: Warga login dan mengirim pengajuan surat SKU
        payload = {
            "jenis_surat": "SKU",
            "keperluan": "Syarat pengajuan KUR BRI"
        }
        res_submit = warga_client.post(
            reverse("surat-ajukan"),
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert res_submit.status_code == 201
        
        # 6: Sistem membuat tiket surat dengan status PENDING
        surat_id = res_submit.json()["data"]["id"]
        assert res_submit.json()["data"]["status"] == "PENDING"

        # 7: Admin memverifikasi data (Status -> VERIFIED)
        res_verify = admin_client.post(
            reverse("surat-proses", kwargs={"surat_id": surat_id}),
            data=json.dumps({"status": "VERIFIED", "notes": "Data lengkap"}),
            content_type="application/json"
        )
        assert res_verify.status_code == 200

        # 8: Admin memproses surat (Status -> PROCESSED)
        res_process = admin_client.post(
            reverse("surat-proses", kwargs={"surat_id": surat_id}),
            data=json.dumps({"status": "PROCESSED"}),
            content_type="application/json"
        )
        assert res_process.status_code == 200

        # 9 & 10: Admin menyelesaikan surat, sistem menghasilkan PDF (Status -> DONE)
        res_done = admin_client.post(
            reverse("surat-proses", kwargs={"surat_id": surat_id}),
            data=json.dumps({"status": "DONE"}),
            content_type="application/json"
        )
        assert res_done.status_code == 200
        assert res_done.json()["data"]["status"] == "DONE"

        # 11: Warga melihat status dan (link) PDF tersedia
        res_check = warga_client.get(reverse("surat-detail", kwargs={"surat_id": surat_id}))
        assert res_check.status_code == 200
        
        surat_data = res_check.json()["data"]
        assert surat_data["status"] == "DONE"
        assert surat_data["pdf_url"] is not None  # Memastikan PDF berhasil di-generate


    # =====================================================================
    # 8.2 Flow Pengaduan oleh Warga
    # =====================================================================
    def test_flow_pengaduan_warga(self, warga_client, admin_client):
        """Menguji Flow 8.2: Warga lapor -> Admin review & proses -> Selesai dengan catatan"""

        # 1 & 2 & 3 & 4 & 5: Warga login dan membuat pengaduan (Status -> OPEN)
        # Catatan: Kita menggunakan POST data biasa (bukan JSON) karena form menerima Multipart/Image
        res_submit = warga_client.post(
            reverse("pengaduan-buat"),
            data={
                "kategori": "Infrastruktur",
                "judul": "Lampu Jalan Mati",
                "deskripsi": "Lampu jalan di RT 01 RW 02 mati sejak 3 hari lalu."
            }
            # foto_bukti dikosongkan karena opsional di PRD
        )
        assert res_submit.status_code == 201
        
        pengaduan_id = res_submit.json()["data"]["id"]
        assert res_submit.json()["data"]["status"] == "OPEN"

        # 6: Admin meninjau dan memberi kategori/penanganan (Status -> TRIAGED)
        res_triage = admin_client.post(
            reverse("pengaduan-proses", kwargs={"pengaduan_id": pengaduan_id}),
            data=json.dumps({"status": "TRIAGED", "notes": "Akan diteruskan ke Kaur Pembangunan"}),
            content_type="application/json"
        )
        assert res_triage.status_code == 200

        # 7: Admin mengubah status sesuai progres (Status -> IN_PROGRESS)
        admin_client.post(
            reverse("pengaduan-proses", kwargs={"pengaduan_id": pengaduan_id}),
            data=json.dumps({"status": "IN_PROGRESS", "notes": "Sedang diperbaiki oleh teknisi"}),
            content_type="application/json"
        )

        # Admin menutup pengaduan (Status -> RESOLVED) dengan catatan wajib
        res_resolved = admin_client.post(
            reverse("pengaduan-proses", kwargs={"pengaduan_id": pengaduan_id}),
            data=json.dumps({
                "status": "RESOLVED", 
                "notes": "Lampu sudah diganti dengan bohlam LED baru dan menyala."
            }),
            content_type="application/json"
        )
        assert res_resolved.status_code == 200

        # 8: Warga memantau status dan catatan tindak lanjut
        res_check = warga_client.get(reverse("pengaduan-detail", kwargs={"pengaduan_id": pengaduan_id}))
        assert res_check.status_code == 200
        
        pengaduan_data = res_check.json()["data"]
        assert pengaduan_data["status"] == "RESOLVED"
        
        # Mengecek apakah histori catatan admin terbaca oleh warga
        histori = pengaduan_data["histori"]
        catatan_terakhir = histori[0]["notes"] # Order descending by created_at
        assert "Lampu sudah diganti" in catatan_terakhir


    # =====================================================================
    # 8.3 Flow Publikasi Berita
    # =====================================================================
    def test_flow_publikasi_berita(self, admin_client, admin):
        """Menguji Flow 8.3: Admin buat DRAFT -> Warga tidak bisa lihat -> Admin PUBLISH -> Warga bisa lihat"""
        
        client_anonim = Client() # Warga publik tidak perlu login untuk baca berita

        # 1 & 2 & 3: Admin login dan membuat berita baru sebagai DRAFT
        res_draft = admin_client.post(
            reverse("publikasi-admin-buat"),
            data=json.dumps({
                "judul": "Bantuan Langsung Tunai Cair",
                "konten_html": "<p>BLT bulan ini akan cair besok.</p>",
                "jenis": "BERITA",
                "status": "DRAFT"
            }),
            content_type="application/json"
        )
        assert res_draft.status_code == 201
        slug_berita = res_draft.json()["slug"]

        # Memastikan DRAFT tidak muncul di portal publik warga
        res_cek_draft = client_anonim.get(reverse("publikasi-detail", kwargs={"slug": slug_berita}))
        assert res_cek_draft.status_code == 404 # Karena belum di-publish

        # 4: Admin review dan publish
        # (Menggunakan service secara langsung karena endpoint ubah_status tidak diekspos di views sebelumnya)
        pub_service = PublikasiService()
        pub_service.ubah_status(actor=admin, slug=slug_berita, new_status="PUBLISHED")

        # 5: Warga (publik) melihat berita pada portal publik
        res_cek_published = client_anonim.get(reverse("publikasi-detail", kwargs={"slug": slug_berita}))
        assert res_cek_published.status_code == 200
        
        berita_data = res_cek_published.json()["data"]
        assert berita_data["judul"] == "Bantuan Langsung Tunai Cair"
        assert "status" not in berita_data 
        
        assert berita_data["published_at"] is not None