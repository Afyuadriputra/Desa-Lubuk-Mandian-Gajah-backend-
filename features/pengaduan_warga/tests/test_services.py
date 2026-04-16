import pytest
from unittest.mock import Mock

from features.pengaduan_warga.domain import STATUS_OPEN, STATUS_TRIAGED
from features.pengaduan_warga.services import PengaduanService, PermissionDeniedError
from features.pengaduan_warga.models import LayananPengaduan

from django.core.exceptions import ValidationError
from features.pengaduan_warga.services import FileUploadError

class TestPengaduanService:
    """Menguji use case pada layer Service dengan teknik mocking."""

    @pytest.fixture
    def mock_repo(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def service(self, mock_repo):
        return PengaduanService(repository=mock_repo)

    @pytest.fixture
    def mock_warga(self, mocker):
        # Memalsukan objek User (Warga)
        user = mocker.Mock()
        user.id = 1
        user.role = "WARGA"
        user.is_authenticated = True
        user.is_active = True
        return user

    @pytest.fixture
    def mock_admin(self, mocker):
        # Memalsukan objek User (Admin)
        user = mocker.Mock()
        user.id = 2
        user.role = "ADMIN"
        user.is_authenticated = True
        user.is_active = True
        return user

    def test_warga_bisa_buat_pengaduan(self, service, mock_warga, mock_repo, mocker):
        """Test: Warga dengan akses valid dapat membuat pengaduan, dan fungsi repository dipanggil."""
        # Mocking audit_event agar tidak error saat dipanggil
        mocker.patch("features.pengaduan_warga.services.audit_event")
        
        # Setup nilai kembalian repository
        mock_pengaduan = Mock(spec=LayananPengaduan, id=100)
        mock_repo.create_pengaduan.return_value = mock_pengaduan

        # Eksekusi
        result = service.buat_pengaduan(
            actor=mock_warga, 
            kategori="Layanan", 
            judul="KTP Lama", 
            deskripsi="Pembuatan KTP saya sudah 1 bulan belum selesai."
        )

        # Verifikasi
        assert result.id == 100
        mock_repo.create_pengaduan.assert_called_once()

    def test_admin_tidak_bisa_buat_pengaduan(self, service, mock_admin):
        """Test: Admin desa seharusnya tidak boleh membuat pengaduan warga."""
        with pytest.raises(PermissionDeniedError, match="Hanya warga yang dapat membuat pengaduan"):
            service.buat_pengaduan(
                actor=mock_admin, 
                kategori="Tes", 
                judul="Judul tes", 
                deskripsi="Deskripsi tes panjang"
            )

    def test_warga_tidak_bisa_lihat_pengaduan_warga_lain(self, service, mock_warga, mock_repo, mocker):
        """Test: Mencegah celah IDOR saat Warga A mengakses detail Warga B."""
        # Setup mock pengaduan dengan ID pelapor yang BEDA dari mock_warga.id (1)
        mock_pengaduan = mocker.Mock()
        mock_pengaduan.pelapor_id = 999 
        mock_repo.get_by_id.return_value = mock_pengaduan

        with pytest.raises(PermissionDeniedError, match="Anda tidak memiliki akses ke pengaduan ini"):
            service.get_pengaduan_detail(mock_warga, pengaduan_id=10)

    def test_upload_file_melebihi_batas_ditolak(self, service, mock_warga, mocker):
        """Test: Memastikan validasi file upload dari toolbox mengembalikan FileUploadError."""
        mock_file = mocker.Mock()
        # Memalsukan (mock) fungsi validasi toolbox agar me-raise ValidationError bawaan Django
        mocker.patch(
            "features.pengaduan_warga.services.validate_image_upload",
            side_effect=ValidationError("Ukuran file maksimal 5 MB.")
        )

        with pytest.raises(FileUploadError, match="Ukuran file maksimal 5 MB"):
            service.buat_pengaduan(
                actor=mock_warga,
                kategori="Umum",
                judul="Judul pengaduan tes",
                deskripsi="Deskripsi pengaduan yang cukup panjang",
                foto_bukti=mock_file
            )

    def test_audit_dan_history_dipanggil_saat_proses(self, service, mock_admin, mock_repo, mocker):
        """Test: Memastikan log audit dan update DB terpanggil saat status berubah."""
        # Mocking audit_event
        mock_audit = mocker.patch("features.pengaduan_warga.services.audit_event")
        
        # Setup data pengaduan awal
        mock_pengaduan = mocker.Mock(status=STATUS_OPEN, id=55)
        mock_repo.get_by_id.return_value = mock_pengaduan
        
        # Eksekusi
        service.proses_pengaduan(
            actor=mock_admin, 
            pengaduan_id=55, 
            new_status=STATUS_TRIAGED, 
            notes="Berkas diterima"
        )
        
        # Verifikasi: Pastikan repository.update_status dipanggil dengan argumen yang benar
        mock_repo.update_status.assert_called_once_with(
            pengaduan=mock_pengaduan, 
            new_status=STATUS_TRIAGED, 
            actor_id=mock_admin.id, 
            notes="Berkas diterima"
        )
        # Verifikasi: Pastikan logger audit dari toolbox terpanggil
        mock_audit.assert_called_once()