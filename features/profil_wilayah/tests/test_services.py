import pytest
from features.profil_wilayah.services import (
    DusunService,
    ProfilWilayahAccessError,
)

class TestDusunService:
    @pytest.fixture
    def mock_repo(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def service(self, mock_repo):
        # Menerapkan Dependency Inversion dengan meng-inject Mock Repository
        return DusunService(repo=mock_repo)

    @pytest.fixture
    def mock_admin(self, mocker):
        user = mocker.Mock(id=1, role="ADMIN")
        return user

    def test_tambah_dusun_harus_sukses_untuk_admin(self, service, mock_admin, mock_repo, mocker):
        # Arrange
        mocker.patch("features.profil_wilayah.services.can_manage_data_wilayah", return_value=True)
        mock_audit = mocker.patch("features.profil_wilayah.services.audit_event")
        mock_repo.create.return_value = mocker.Mock(id=10)

        # Act
        hasil = service.tambah_dusun(mock_admin, nama_dusun="Mawar", kepala_dusun="Budi")

        # Assert
        assert hasil.id == 10
        mock_repo.create.assert_called_once_with("Mawar", "Budi")
        mock_audit.assert_called_once_with("DUSUN_CREATED", actor_id=1, target_id=10)

    def test_tambah_dusun_harus_ditolak_jika_tidak_punya_izin(self, service, mock_admin, mocker):
        mocker.patch("features.profil_wilayah.services.can_manage_data_wilayah", return_value=False)

        with pytest.raises(ProfilWilayahAccessError, match="Akses ditolak"):
            service.tambah_dusun(mock_admin, nama_dusun="Mawar", kepala_dusun="Budi")