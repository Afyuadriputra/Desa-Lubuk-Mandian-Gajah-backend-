import pytest
from django.core.exceptions import ValidationError
from features.potensi_ekonomi.domain import KATEGORI_WISATA
from features.potensi_ekonomi.models import BumdesUnitUsaha
from features.potensi_ekonomi.services import (
    FileUploadError,
    PermissionDeniedError,
    PotensiEkonomiService,
    UnitUsahaNotFoundError,
)

class TestPotensiEkonomiService:
    @pytest.fixture
    def mock_repo(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def service(self, mock_repo):
        return PotensiEkonomiService(repository=mock_repo)

    @pytest.fixture
    def mock_admin(self, mocker):
        user = mocker.Mock()
        user.id = 1
        user.role = "ADMIN" # Asumsi role admin bisa manage
        user.is_authenticated = True
        user.is_active = True
        return user

    @pytest.fixture
    def mock_warga(self, mocker):
        user = mocker.Mock()
        user.id = 2
        user.role = "WARGA"
        user.is_authenticated = True
        user.is_active = True
        return user

    def test_warga_tidak_bisa_buat_unit_usaha(self, service, mock_warga):
        with pytest.raises(PermissionDeniedError, match="Anda tidak memiliki izin"):
            service.buat_unit_usaha(mock_warga, {"nama_usaha": "Taman", "kategori": KATEGORI_WISATA})

    def test_sanitasi_html_diterapkan_untuk_cegah_xss(self, service, mock_admin, mock_repo, mocker):
        """Test: Input dengan script jahat harus dibersihkan sebelum masuk DB."""
        mocker.patch("features.potensi_ekonomi.services.audit_event")
        # PERBAIKAN: Kita mock can_manage_data_bumdes di tempat ia DIPAKAI (services)
        mocker.patch("features.potensi_ekonomi.services.can_manage_data_bumdes", return_value=True)
        
        # Buat kembalian palsu dari repository
        mock_repo.create_unit.return_value = mocker.Mock(id=1, nama_usaha="Taman")
        
        # Ini adalah variabel data_kotor yang sempat hilang
        data_kotor = {
            "nama_usaha": "Taman Indah",
            "kategori": KATEGORI_WISATA,
            "deskripsi": "<script>alert('XSS')</script><p>Deskripsi aman</p>"
        }
        
        service.buat_unit_usaha(mock_admin, data_kotor)
        
        # Ambil argumen yang dikirim ke repository
        args, _ = mock_repo.create_unit.call_args
        data_tersimpan = args[0]
        
        # Script tag jahat harus terhapus dari deskripsi
        assert "<script>" not in data_tersimpan["deskripsi"]

    def test_warga_tidak_bisa_lihat_detail_draft(self, service, mock_warga, mock_repo, mocker):
        """Test: Mencegah Warga melihat Unit Usaha yang is_published=False."""
        mocker.patch("features.potensi_ekonomi.permissions.can_manage_data_bumdes", return_value=False)
        mocker.patch("features.potensi_ekonomi.permissions.can_view_katalog_publik", return_value=True)
        
        mock_draft = mocker.Mock(is_published=False)
        mock_repo.get_by_id.return_value = mock_draft

        with pytest.raises(PermissionDeniedError, match="belum tersedia untuk publik"):
            service.get_detail_unit(mock_warga, unit_id=99)