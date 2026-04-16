# features/layanan_administrasi/tests/test_repositories.py

import pytest
from django.contrib.auth import get_user_model

from features.layanan_administrasi.repositories import SuratRepository
from features.layanan_administrasi.models import LayananSurat

User = get_user_model()


@pytest.mark.django_db
class TestCreateSuratRepository:
    def test_should_create_surat_and_initial_history(self):
        """Harus membuat surat + 1 histori awal (PENDING)"""

        user = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="Warga",
            role="WARGA",
        )

        repo = SuratRepository()

        surat = repo.create_surat(
            pemohon_id=user.id,
            jenis_surat="SKU",
            keperluan="Untuk keperluan usaha toko"
        )

        assert surat is not None
        assert surat.status == "PENDING"
        assert surat.pemohon_id == user.id

        #  cek histori
        histories = surat.histori_status.all()
        assert histories.count() == 1

        history = histories.first()
        assert history.status_from is None
        assert history.status_to == "PENDING"
        assert history.changed_by_id == user.id


@pytest.mark.django_db
class TestUpdateStatusRepository:
    def test_should_update_status_and_create_history(self):
        """Setiap update status harus membuat histori baru"""

        user = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="Warga",
            role="WARGA",
        )

        repo = SuratRepository()

        surat = repo.create_surat(
            pemohon_id=user.id,
            jenis_surat="SKU",
            keperluan="Untuk usaha"
        )

        updated = repo.update_status(
            surat=surat,
            new_status="VERIFIED",
            actor_id=user.id
        )

        assert updated.status == "VERIFIED"

        #  histori harus nambah
        assert updated.histori_status.count() == 2


    def test_should_store_nomor_surat_when_provided(self):
        """Nomor surat harus tersimpan jika diberikan"""

        user = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="Admin",
            role="ADMIN",
        )

        repo = SuratRepository()

        surat = repo.create_surat(
            pemohon_id=user.id,
            jenis_surat="SKU",
            keperluan="Untuk usaha"
        )

        updated = repo.update_status(
            surat=surat,
            new_status="PROCESSED",
            actor_id=user.id,
            nomor_surat="470/SKU/IV/2026/ABCD"
        )

        assert updated.nomor_surat == "470/SKU/IV/2026/ABCD"


    def test_should_store_rejection_reason_when_rejected(self):
        """Rejection reason harus tersimpan saat status REJECTED"""

        user = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="Admin",
            role="ADMIN",
        )

        repo = SuratRepository()

        surat = repo.create_surat(
            pemohon_id=user.id,
            jenis_surat="SKU",
            keperluan="Untuk usaha"
        )

        updated = repo.update_status(
            surat=surat,
            new_status="REJECTED",
            actor_id=user.id,
            rejection_reason="Dokumen tidak lengkap"
        )

        assert updated.rejection_reason == "Dokumen tidak lengkap"


    def test_should_not_set_rejection_reason_if_not_rejected(self):
        """Rejection reason tidak boleh tersimpan jika bukan REJECTED"""

        user = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="Admin",
            role="ADMIN",
        )

        repo = SuratRepository()

        surat = repo.create_surat(
            pemohon_id=user.id,
            jenis_surat="SKU",
            keperluan="Untuk usaha"
        )

        updated = repo.update_status(
            surat=surat,
            new_status="VERIFIED",
            actor_id=user.id,
            rejection_reason="Tidak valid"
        )

        assert updated.rejection_reason is None