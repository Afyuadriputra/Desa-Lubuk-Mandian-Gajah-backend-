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

    def test_buat_publikasi_membersihkan_xss_dan_atur_tanggal(self, service, mock_admin, mock_repo, mocker):
        mocker.patch("features.publikasi_informasi.services.can_create_or_edit_publikasi", return_value=True)
        mock_audit = mocker.patch("features.publikasi_informasi.services.audit_event")
        
        mock_repo.create.return_value = mocker.Mock(id=99)
        
        # Test XSS dan status PUBLISHED
        service.buat_publikasi(
            actor=mock_admin,
            judul="Berita Baru",
            konten_html="<script>alert('XSS')</script><p>Aman</p>",
            jenis=JENIS_BERITA,
            status=STATUS_PUBLISHED
        )
        
        # Cek data yang dilempar ke repository
        args, _ = mock_repo.create.call_args
        data_tersimpan = args[0]
        
        assert "<script>" not in data_tersimpan["konten_html"]
        assert data_tersimpan["published_at"] is not None # Karena status PUBLISHED, harus ada tanggal
        mock_audit.assert_called_once()

    # PERBAIKAN: Tambahkan 'mocker' di dalam kurung parameter di bawah ini
    def test_get_detail_publik_menolak_data_draft(self, service, mock_repo, mocker):
        # Setup mock agar repo mengembalikan data bersatus DRAFT
        mock_publikasi = mocker.Mock(status=STATUS_DRAFT)
        mock_repo.get_by_slug.return_value = mock_publikasi
        
        with pytest.raises(PublikasiError, match="belum dipublikasikan"):
            service.get_detail_publik("slug-rahasia")