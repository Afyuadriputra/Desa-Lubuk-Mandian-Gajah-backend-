# tests/test_prd_compliance.py

import json
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

# Import layanan untuk bypass setup data
from features.publikasi_informasi.services import PublikasiService
from features.layanan_administrasi.services import SuratService
from features.potensi_ekonomi.services import PotensiEkonomiService

User = get_user_model()

@pytest.fixture
def user_factory():
    counter = 1
    def create(role="WARGA", is_staff=False):
        nonlocal counter
        nik = str(counter).zfill(16)
        counter += 1
        return User.objects.create_user(
            nik=nik, password="password123", nama_lengkap=f"User {nik}", role=role, is_staff=is_staff
        )
    return create

@pytest.mark.django_db
class TestPRDCompliance:

    # =====================================================================
    # COMPLIANCE 7A: Brute Force Protection (Pembatasan Percobaan Login)
    # Catatan: Ini mengasumsikan django-axes aktif sesuai log terminal Anda
    # =====================================================================
    def test_7a_brute_force_protection_blocks_repeated_failures(self, user_factory):
        """Memastikan percobaan login gagal berulang memicu proteksi keamanan."""
        client = Client()
        warga = user_factory(role="WARGA")
        
        login_url = reverse("auth-login")
        payload_salah = {"nik": warga.nik, "password": "wrongpassword!"}

        # Lakukan percobaan gagal sebanyak 5 kali (batas default django-axes biasanya 3 atau 5)
        for _ in range(5):
            client.post(login_url, data=json.dumps(payload_salah), content_type="application/json")

        # Percobaan ke-6 harusnya di-lockout (Biasanya Axes mengembalikan status 403 Forbidden / 429 Too Many Requests)
        res_lockout = client.post(login_url, data=json.dumps(payload_salah), content_type="application/json")
        
        # Validasi bahwa akses ditolak karena proteksi brute force (bukan sekadar 401 salah password biasa)
        assert res_lockout.status_code in [403, 429] 
        # Jika menggunakan konfigurasi Axes standar yang mengembalikan 403, pastikan responnya bukan 401


    # =====================================================================
    # COMPLIANCE 7C: Sanitasi HTML (Mencegah Serangan XSS)
    # =====================================================================
    def test_7c_konten_berbahaya_dibersihkan_saat_disimpan(self, user_factory):
        """Memastikan tag <script> berbahaya dihapus oleh fungsi sanitasi."""
        admin = user_factory(role="ADMIN", is_staff=True)
        
        # Input HTML berbahaya dari hacker
        malicious_html = '<p>Baca berita ini!</p><script>alert("Hacked!");</script><b>Penting</b>'
        
        pub_service = PublikasiService()
        publikasi = pub_service.buat_publikasi(
            actor=admin,
            judul="Berita Uji XSS",
            konten_html=malicious_html,
            jenis="BERITA",
            status="PUBLISHED"
        )
        
        # Script tag harusnya terhapus (XSS gagal dieksekusi), teks sisanya aman
        assert "<script>" not in publikasi.konten_html
        assert "</script>" not in publikasi.konten_html
        assert "<p>Baca berita ini!</p>" in publikasi.konten_html
        assert "<b>Penting</b>" in publikasi.konten_html


    # =====================================================================
    # COMPLIANCE 7C & 7F: Data Draft Tidak Terlihat Publik
    # =====================================================================
    def test_7c_7f_draft_tidak_terlihat_oleh_publik(self, user_factory):
        """Memastikan warga hanya melihat konten berstatus published/aktif."""
        admin = user_factory(role="ADMIN", is_staff=True)
        warga = user_factory(role="WARGA")
        client_warga = Client()
        client_warga.force_login(warga)

        # Buat data BUMDes Draft
        eko_service = PotensiEkonomiService()
        eko_service.buat_unit_usaha(actor=admin, data={
            "nama_usaha": "Koperasi Draft", "kategori": "KOPERASI", "is_published": False
        })
        # Buat data BUMDes Published
        eko_service.buat_unit_usaha(actor=admin, data={
            "nama_usaha": "Koperasi Aktif", "kategori": "KOPERASI", "is_published": True
        })

        # Cek endpoint publik
        res_katalog = client_warga.get(reverse("ekonomi-katalog"))
        data_katalog = res_katalog.json()["data"]
        
        # Hanya boleh ada 1 yang muncul, dan itu harus "Koperasi Aktif"
        assert len(data_katalog) == 1
        assert data_katalog[0]["nama_usaha"] == "Koperasi Aktif"


    # =====================================================================
    # COMPLIANCE 7D & 7E: Data Isolation (Warga hanya lihat datanya sendiri)
    # =====================================================================
    def test_7d_7e_warga_hanya_melihat_data_sendiri(self, user_factory):
        """Warga A tidak boleh bisa membuka atau melihat surat milik Warga B."""
        warga_a = user_factory(role="WARGA")
        warga_b = user_factory(role="WARGA")
        
        client_b = Client()
        client_b.force_login(warga_b)

        # Warga A membuat surat (keperluan diperpanjang agar lolos validasi > 10 karakter)
        surat_service = SuratService()
        surat_a = surat_service.ajukan_surat(
            actor=warga_a, 
            jenis_surat="SKU", 
            keperluan="Untuk syarat pengajuan pinjaman bank" 
        )

        # Warga B mencoba mengakses detail surat Warga A melalui API
        res_illegal_access = client_b.get(reverse("surat-detail", kwargs={"surat_id": str(surat_a.id)}))
        
        # Harus ditolak (Forbidden / Not Found)
        assert res_illegal_access.status_code in [403, 404]