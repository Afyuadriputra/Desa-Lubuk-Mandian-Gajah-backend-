import pytest
from pytest_mock import mocker
from features.publikasi_informasi.domain import STATUS_DRAFT, STATUS_PUBLISHED, JENIS_BERITA
from features.publikasi_informasi.services import PublikasiService, PublikasiAccessError, PublikasiError

class TestPublikasiService:
    @pytest.fixture
    def mock_repo(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def service(self, mock_repo):
        # Dependency Inversion: Inject mock ke dalam service
        return PublikasiService(repo=mock_repo)

    @pytest.fixture
    def mock_admin(self, mocker):
        return mocker.Mock(id=1)

    def test_buat_publikasi_ditolak_jika_tanpa_akses(self, service, mock_admin, mocker):
        mocker.patch("features.publikasi_informasi.services.can_create_or_edit_publikasi", return_value=False)
        
        with pytest.raises(PublikasiAccessError, match="tidak memiliki izin"):
            service.buat_publikasi(mock_admin, "Judul Valid", "<p>Konten panjang</p>", JENIS_BERITA, STATUS_DRAFT)

    # PERBAIKAN: Tambahkan 'mocker' di dalam kurung parameter di bawah ini
    def test_get_detail_publik_menolak_data_draft(self, service, mock_repo, mocker):
        # Setup mock agar repo mengembalikan data bersatus DRAFT
        mock_publikasi = mocker.Mock(status=STATUS_DRAFT)
        mock_repo.get_by_slug.return_value = mock_publikasi
        
        with pytest.raises(PublikasiError, match="belum dipublikasikan"):
            service.get_detail_publik("slug-rahasia")