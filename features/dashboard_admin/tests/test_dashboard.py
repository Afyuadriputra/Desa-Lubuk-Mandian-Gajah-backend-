# features/dashboard_admin/tests/test_dashboard.py

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

from features.dashboard_admin.services import DashboardService
from features.dashboard_admin.domain import DashboardAccessError
from features.layanan_administrasi.models import LayananSurat
from features.pengaduan_warga.models import LayananPengaduan
from features.potensi_ekonomi.models import BumdesUnitUsaha

User = get_user_model()


# =====================================================================
# 🔹 SETUP FIXTURES (Menyiapkan Data Uji)
# =====================================================================
@pytest.fixture
def users():
    warga1 = User.objects.create_user(nik="1111111111111111", password="pass", nama_lengkap="Warga A", role="WARGA")
    warga2 = User.objects.create_user(nik="2222222222222222", password="pass", nama_lengkap="Warga B", role="WARGA")
    
    # Sesuai Matriks Hak Akses PRD (Admin Desa dan Super Admin)
    admin_desa = User.objects.create_user(nik="3333333333333333", password="pass", nama_lengkap="Admin Desa", role="ADMIN", is_staff=True)
    super_admin = User.objects.create_user(nik="4444444444444444", password="pass", nama_lengkap="Kades", role="SUPERADMIN", is_staff=True, is_superuser=True)
    
    return {"warga": warga1, "warga2": warga2, "admin_desa": admin_desa, "super_admin": super_admin}

@pytest.fixture
def seed_data(users):
    """Membuat data dummy untuk dihitung oleh Dashboard."""
    warga = users["warga"]

    # 1. Buat 3 Surat (2 PENDING, 1 DONE)
    LayananSurat.objects.create(pemohon=warga, jenis_surat="SKU", keperluan="Test 1", status="PENDING")
    LayananSurat.objects.create(pemohon=warga, jenis_surat="SKTM", keperluan="Test 2", status="PENDING")
    LayananSurat.objects.create(pemohon=warga, jenis_surat="Domisili", keperluan="Test 3", status="DONE")

    # 2. Buat 3 Pengaduan (2 Infrastruktur OPEN, 1 Pelayanan RESOLVED)
    LayananPengaduan.objects.create(pelapor=warga, kategori="Infrastruktur", judul="Jalan Rusak", deskripsi="Test", status="OPEN")
    LayananPengaduan.objects.create(pelapor=warga, kategori="Infrastruktur", judul="Jembatan", deskripsi="Test", status="OPEN")
    LayananPengaduan.objects.create(pelapor=warga, kategori="Pelayanan", judul="KTP Lambat", deskripsi="Test", status="RESOLVED")

    # 3. Buat 2 BUMDes (1 Published, 1 Draft)
    BumdesUnitUsaha.objects.create(nama_usaha="Koperasi A", kategori="KOPERASI", deskripsi="Test", is_published=True)
    BumdesUnitUsaha.objects.create(nama_usaha="Wisata B", kategori="WISATA", deskripsi="Test", is_published=False)


# =====================================================================
# 🔹 TEST 1: KEPATUHAN HAK AKSES (PRD Bagian 5 & 9)
# =====================================================================
@pytest.mark.django_db
class TestDashboardPermissions:
    
    def test_warga_tidak_bisa_melihat_dashboard(self, users):
        """Memastikan role WARGA ditolak saat mengakses dashboard service."""
        service = DashboardService()
        warga = users["warga"]
        
        with pytest.raises(Exception): # Menangkap DashboardAccessError / PermissionDeniedError
            service.get_analitik_lengkap(actor=warga)

    def test_admin_desa_bisa_melihat_dashboard(self, users, seed_data):
        """Memastikan Admin Desa memiliki izin melihat analitik."""
        service = DashboardService()
        admin = users["admin_desa"]
        
        data = service.get_analitik_lengkap(actor=admin)
        assert "summary" in data

    def test_super_admin_bisa_melihat_dashboard(self, users, seed_data):
        """Memastikan Super Admin memiliki izin melihat analitik."""
        service = DashboardService()
        super_admin = users["super_admin"]
        
        data = service.get_analitik_lengkap(actor=super_admin)
        assert "summary" in data


# =====================================================================
# 🔹 TEST 2: AKURASI AGREGASI DATA (PRD Bagian 6.2)
# =====================================================================
@pytest.mark.django_db
class TestDashboardAnalytics:

    def test_summary_metrics_dihitung_dengan_benar(self, users, seed_data):
        """Memastikan widget ringkasan menampilkan angka yang tepat."""
        service = DashboardService()
        admin = users["admin_desa"]
        
        data = service.get_analitik_lengkap(actor=admin)
        summary = data["summary"]

        # Ada 2 warga yang dibuat di fixture 'users'
        assert summary["total_warga_aktif"] == 2 
        
        # Hanya ada 2 surat yang statusnya PENDING
        assert summary["surat_pending"] == 2 
        
        # Ada 2 pengaduan yang masih OPEN/TRIAGED/IN_PROGRESS
        assert summary["pengaduan_aktif"] == 2 
        
        # Ada 1 BUMDes yang is_published=True
        assert summary["bumdes_published"] == 1 

    def test_grafik_surat_dikelompokkan_berdasarkan_status(self, users, seed_data):
        """Memastikan data untuk Donut Chart Surat valid."""
        service = DashboardService()
        admin = users["admin_desa"]
        
        data = service.get_analitik_lengkap(actor=admin)
        surat_stats = data["charts"]["surat_by_status"]

        # Mengubah list of dict menjadi dictionary mudah dibaca {'PENDING': 2, 'DONE': 1}
        stats_dict = {item['status']: item['total'] for item in surat_stats}
        
        assert stats_dict["PENDING"] == 2
        assert stats_dict["DONE"] == 1

    def test_grafik_pengaduan_dikelompokkan_berdasarkan_kategori(self, users, seed_data):
        """Memastikan data untuk Bar Chart Pengaduan valid."""
        service = DashboardService()
        admin = users["admin_desa"]
        
        data = service.get_analitik_lengkap(actor=admin)
        pengaduan_stats = data["charts"]["pengaduan_by_kategori"]

        stats_dict = {item['kategori']: item['total'] for item in pengaduan_stats}
        
        assert stats_dict["Infrastruktur"] == 2
        assert stats_dict["Pelayanan"] == 1