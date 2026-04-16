import pytest
from django.contrib.auth import get_user_model

from features.pengaduan_warga.repositories import PengaduanRepository
from features.pengaduan_warga.domain import STATUS_OPEN, STATUS_IN_PROGRESS
from features.pengaduan_warga.models import LayananPengaduanHistory

# Gunakan CustomUser model sesuai PRD
User = get_user_model()

# Tandai seluruh file ini untuk menggunakan database testing
pytestmark = pytest.mark.django_db

class TestPengaduanRepository:
    """Menguji interaksi langsung dengan Database PostgreSQL/SQLite testing."""

    def test_create_dan_update_status_mencatat_histori_db(self):
        """Test: Transaksi DB menyimpan pengaduan dan melacak histori dengan akurat."""
        # 1. Setup User (Asumsi field minimal sesuai CustomUser PRD)
        pelapor = User.objects.create(nik="11112222", nama_lengkap="Warga A", role="WARGA")
        admin = User.objects.create(nik="99998888", nama_lengkap="Admin A", role="ADMIN")
        
        repo = PengaduanRepository()
        
        # 2. Test Eksekusi: Buat Pengaduan
        pengaduan = repo.create_pengaduan(
            pelapor_id=pelapor.id,
            kategori="Infrastruktur",
            judul="Jalan Rusak",
            deskripsi="Deskripsi jalan rusak panjang."
        )
        assert pengaduan.status == STATUS_OPEN
        
        # Verifikasi Histori Awal: Harus ada 1 record "Created"
        histori_awal = LayananPengaduanHistory.objects.filter(pengaduan=pengaduan)
        assert histori_awal.count() == 1
        assert histori_awal.first().status_to == STATUS_OPEN
        
        # 3. Test Eksekusi: Update Status oleh Admin
        repo.update_status(
            pengaduan=pengaduan, 
            new_status=STATUS_IN_PROGRESS, 
            actor_id=admin.id, 
            notes="Tim sedang meluncur ke lokasi"
        )
        
        # Verifikasi Histori Akhir: Harus bertambah menjadi 2 record
        histori_akhir = LayananPengaduanHistory.objects.filter(pengaduan=pengaduan).order_by("-created_at")
        assert histori_akhir.count() == 2
        
        # Verifikasi detail log terakhir
        log_terbaru = histori_akhir.first()
        assert log_terbaru.status_from == STATUS_OPEN
        assert log_terbaru.status_to == STATUS_IN_PROGRESS
        assert log_terbaru.notes == "Tim sedang meluncur ke lokasi"
        assert log_terbaru.changed_by_id == admin.id