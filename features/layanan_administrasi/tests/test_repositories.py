# features/layanan_administrasi/tests/test_repositories.py

import pytest
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from features.layanan_administrasi.models import TemplateSurat
from features.layanan_administrasi.repositories import (
    SuratRepository,
    TemplateSuratRepository,
)

User = get_user_model()


@pytest.mark.django_db
class TestTemplateSuratRepository:
    def test_should_create_template(self, uploaded_docx_file):
        repo = TemplateSuratRepository()

        template = repo.create_template(
            kode=" sku ",
            nama="Surat Keterangan Usaha",
            deskripsi="Template surat usaha.",
            file_template=uploaded_docx_file,
            is_active=True,
        )

        assert template.id is not None
        assert template.kode == "SKU"
        assert template.is_active is True

    def test_should_get_active_template_by_id(self, template_surat_aktif):
        repo = TemplateSuratRepository()

        template = repo.get_active_by_id(template_surat_aktif.id)

        assert template is not None
        assert template.id == template_surat_aktif.id

    def test_should_not_get_inactive_template_as_active(self, template_surat_nonaktif):
        repo = TemplateSuratRepository()

        template = repo.get_active_by_id(template_surat_nonaktif.id)

        assert template is None

    def test_should_get_template_by_normalized_kode(self, template_surat_aktif):
        repo = TemplateSuratRepository()

        template = repo.get_by_kode(" sku ")

        assert template is not None
        assert template.id == template_surat_aktif.id

    def test_should_list_only_active_templates(self, template_surat_aktif, template_surat_nonaktif):
        repo = TemplateSuratRepository()

        templates = repo.list_active()

        assert template_surat_aktif in templates
        assert template_surat_nonaktif not in templates

    def test_should_update_template_metadata(self, template_surat_aktif):
        repo = TemplateSuratRepository()

        updated = repo.update_template(
            template=template_surat_aktif,
            nama="Surat Usaha Updated",
            deskripsi="Updated",
            is_active=False,
        )

        assert updated.nama == "Surat Usaha Updated"
        assert updated.deskripsi == "Updated"
        assert updated.is_active is False

    def test_should_delete_template(self, template_surat_aktif):
        repo = TemplateSuratRepository()
        template_id = template_surat_aktif.id

        repo.delete_template(template_surat_aktif)

        assert TemplateSurat.objects.filter(id=template_id).exists() is False


@pytest.mark.django_db
class TestCreateSuratRepository:
    def test_should_create_surat_with_template_and_initial_history(self, warga_user, template_surat_aktif):
        repo = SuratRepository()

        surat = repo.create_surat(
            pemohon_id=warga_user.id,
            template=template_surat_aktif,
            keperluan="Untuk keperluan usaha toko",
        )

        assert surat is not None
        assert surat.status == "PENDING"
        assert surat.pemohon_id == warga_user.id
        assert surat.template_id == template_surat_aktif.id
        assert surat.jenis_surat == template_surat_aktif.kode
        assert surat.histori_status.count() == 1

    def test_should_still_create_legacy_surat_without_template(self, warga_user):
        repo = SuratRepository()

        surat = repo.create_surat(
            pemohon_id=warga_user.id,
            jenis_surat="SKU",
            keperluan="Untuk keperluan usaha toko",
        )

        assert surat.template_id is None
        assert surat.jenis_surat == "SKU"
        assert surat.status == "PENDING"


@pytest.mark.django_db
class TestUpdateStatusRepository:
    def test_should_update_status_and_create_history(self, warga_user):
        repo = SuratRepository()
        surat = repo.create_surat(
            pemohon_id=warga_user.id,
            jenis_surat="SKU",
            keperluan="Untuk usaha toko warga",
        )

        updated = repo.update_status(
            surat=surat,
            new_status="VERIFIED",
            actor_id=warga_user.id,
        )

        assert updated.status == "VERIFIED"
        assert updated.histori_status.count() == 2

    def test_should_store_nomor_surat_when_provided(self, admin_user):
        repo = SuratRepository()
        surat = repo.create_surat(
            pemohon_id=admin_user.id,
            jenis_surat="SKU",
            keperluan="Untuk usaha toko warga",
        )

        updated = repo.update_status(
            surat=surat,
            new_status="PROCESSED",
            actor_id=admin_user.id,
            nomor_surat="470/SKU/IV/2026/ABCD",
        )

        assert updated.nomor_surat == "470/SKU/IV/2026/ABCD"

    def test_should_store_rejection_reason_when_rejected(self, admin_user):
        repo = SuratRepository()
        surat = repo.create_surat(
            pemohon_id=admin_user.id,
            jenis_surat="SKU",
            keperluan="Untuk usaha toko warga",
        )

        updated = repo.update_status(
            surat=surat,
            new_status="REJECTED",
            actor_id=admin_user.id,
            rejection_reason="Dokumen tidak lengkap",
        )

        assert updated.rejection_reason == "Dokumen tidak lengkap"

    def test_should_not_set_rejection_reason_if_not_rejected(self, admin_user):
        repo = SuratRepository()
        surat = repo.create_surat(
            pemohon_id=admin_user.id,
            jenis_surat="SKU",
            keperluan="Untuk usaha toko warga",
        )

        updated = repo.update_status(
            surat=surat,
            new_status="VERIFIED",
            actor_id=admin_user.id,
            rejection_reason="Tidak valid",
        )

        assert updated.rejection_reason is None

    def test_should_save_generated_docx(self, warga_user):
        repo = SuratRepository()
        surat = repo.create_surat(
            pemohon_id=warga_user.id,
            jenis_surat="SKU",
            keperluan="Untuk usaha toko warga",
        )

        updated = repo.save_generated_docx(
            surat=surat,
            filename="surat-test.docx",
            content_file=ContentFile(b"DOCX"),
        )

        assert updated.docx_file.name.endswith(".docx")