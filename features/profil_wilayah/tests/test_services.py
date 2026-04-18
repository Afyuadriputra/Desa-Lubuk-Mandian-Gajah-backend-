import pytest
from features.profil_wilayah.services import (
    DusunService,
    PerangkatService,
    ProfilWilayahAccessError,
)

class TestDusunService:
    @pytest.fixture
    def mock_repo(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def service(self, mock_repo):
        return DusunService(repo=mock_repo)

    @pytest.fixture
    def mock_admin(self, mocker):
        return mocker.Mock(id=1, role="ADMIN")

    def test_tambah_dusun_harus_sukses_untuk_admin(self, service, mock_admin, mock_repo, mocker):
        mocker.patch("features.profil_wilayah.services.can_manage_data_wilayah", return_value=True)
        mock_audit = mocker.patch("features.profil_wilayah.services.audit_event")
        mock_repo.create.return_value = mocker.Mock(id=10)

        hasil = service.tambah_dusun(mock_admin, nama_dusun="Mawar", kepala_dusun="Budi")

        assert hasil.id == 10
        mock_repo.create.assert_called_once_with("Mawar", "Budi")
        mock_audit.assert_called_once_with("DUSUN_CREATED", actor_id=1, target_id=10)

    def test_ubah_dusun_harus_sukses_untuk_admin(self, service, mock_admin, mock_repo, mocker):
        mocker.patch("features.profil_wilayah.services.can_manage_data_wilayah", return_value=True)
        mock_audit = mocker.patch("features.profil_wilayah.services.audit_event")
        mock_repo.update.return_value = mocker.Mock(id=11, nama_dusun="Melati")

        hasil = service.ubah_dusun(mock_admin, dusun_id=11, nama_dusun="Melati", kepala_dusun="Joko")

        assert hasil.id == 11
        mock_repo.update.assert_called_once_with(11, "Melati", "Joko")
        mock_audit.assert_called_once_with("DUSUN_UPDATED", actor_id=1, target_id=11)

    def test_hapus_dusun_harus_sukses_untuk_admin(self, service, mock_admin, mock_repo, mocker):
        mocker.patch("features.profil_wilayah.services.can_manage_data_wilayah", return_value=True)
        mock_audit = mocker.patch("features.profil_wilayah.services.audit_event")

        service.hapus_dusun(mock_admin, dusun_id=12)

        mock_repo.delete.assert_called_once_with(12)
        mock_audit.assert_called_once_with("DUSUN_DELETED", actor_id=1, target_id=12)

    def test_tambah_dusun_harus_ditolak_jika_tidak_punya_izin(self, service, mock_admin, mocker):
        mocker.patch("features.profil_wilayah.services.can_manage_data_wilayah", return_value=False)

        with pytest.raises(ProfilWilayahAccessError, match="Akses ditolak"):
            service.tambah_dusun(mock_admin, nama_dusun="Mawar", kepala_dusun="Budi")


class TestPerangkatService:
    @pytest.fixture
    def mock_repo(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def service(self, mock_repo):
        return PerangkatService(repo=mock_repo)

    @pytest.fixture
    def mock_admin(self, mocker):
        return mocker.Mock(id=1, role="ADMIN")

    def test_tambah_perangkat_harus_sukses_untuk_admin(self, service, mock_admin, mock_repo, mocker):
        mocker.patch("features.profil_wilayah.services.can_manage_data_wilayah", return_value=True)
        mocker.patch("features.profil_wilayah.services.validate_image_upload")
        mock_audit = mocker.patch("features.profil_wilayah.services.audit_event")
        mock_repo.create.return_value = mocker.Mock(id=20)

        hasil = service.tambah_perangkat(
            actor=mock_admin,
            user_id="abc",
            jabatan="Sekdes",
            is_published=True,
            foto=mocker.Mock(),
        )

        assert hasil.id == 20
        mock_repo.create.assert_called_once()
        mock_audit.assert_called_once_with("PERANGKAT_CREATED", actor_id=1, target_id=20)

    def test_ubah_perangkat_harus_sukses_untuk_admin(self, service, mock_admin, mock_repo, mocker):
        mocker.patch("features.profil_wilayah.services.can_manage_data_wilayah", return_value=True)
        mocker.patch("features.profil_wilayah.services.validate_image_upload")
        mock_audit = mocker.patch("features.profil_wilayah.services.audit_event")
        mock_repo.update.return_value = mocker.Mock(id=21)

        hasil = service.ubah_perangkat(
            actor=mock_admin,
            perangkat_id=21,
            user_id="def",
            jabatan="Kaur",
            is_published=False,
            foto=mocker.Mock(),
        )

        assert hasil.id == 21
        mock_repo.update.assert_called_once()
        mock_audit.assert_called_once_with("PERANGKAT_UPDATED", actor_id=1, target_id=21)

    def test_hapus_perangkat_harus_sukses_untuk_admin(self, service, mock_admin, mock_repo, mocker):
        mocker.patch("features.profil_wilayah.services.can_manage_data_wilayah", return_value=True)
        mock_audit = mocker.patch("features.profil_wilayah.services.audit_event")

        service.hapus_perangkat(mock_admin, perangkat_id=22)

        mock_repo.delete.assert_called_once_with(22)
        mock_audit.assert_called_once_with("PERANGKAT_DELETED", actor_id=1, target_id=22)

    def test_tambah_perangkat_harus_ditolak_jika_tidak_punya_izin(self, service, mock_admin, mocker):
        mocker.patch("features.profil_wilayah.services.can_manage_data_wilayah", return_value=False)

        with pytest.raises(ProfilWilayahAccessError, match="Akses ditolak"):
            service.tambah_perangkat(
                actor=mock_admin,
                user_id="abc",
                jabatan="Sekdes",
                is_published=True,
            )