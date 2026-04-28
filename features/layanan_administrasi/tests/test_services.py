# features/layanan_administrasi/tests/test_services.py

import pytest
from unittest.mock import patch

from django.contrib.auth import get_user_model

from features.layanan_administrasi.domain import (
    JENIS_SKU,
    STATUS_DONE,
    STATUS_PROCESSED,
    STATUS_REJECTED,
    STATUS_VERIFIED,
    InvalidStatusTransitionError,
    RejectionReasonRequiredError,
)
from features.layanan_administrasi.services import (
    PermissionDeniedError,
    SuratDocumentRenderer,
    SuratService,
    TemplateSuratNotFoundError,
    TemplateSuratService,
)

User = get_user_model()


class FakeDocumentRenderer:
    def render_docx(self, template_path: str, context: dict) -> bytes:
        return b"FAKE-DOCX-CONTENT"


@pytest.fixture
def user_factory(db):
    counter = 1

    def create(role="WARGA", is_staff=False, is_superuser=False):
        nonlocal counter
        nik = str(counter).zfill(16)
        counter += 1

        return User.objects.create_user(
            nik=nik,
            password="pass",
            nama_lengkap=f"User {nik}",
            role=role,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )

    return create


@pytest.fixture
def surat_setup(user_factory, template_surat_aktif):
    warga = user_factory(role="WARGA")
    admin = user_factory(role="ADMIN", is_staff=True)

    service = SuratService(document_renderer=FakeDocumentRenderer())
    surat = service.repository.create_surat(
        pemohon_id=warga.id,
        template=template_surat_aktif,
        keperluan="Keperluan panjang sekali untuk usaha",
    )

    return warga, admin, service, surat


@pytest.mark.django_db
class TestTemplateSuratService:
    def test_admin_should_create_template(self, admin_user, uploaded_docx_file):
        service = TemplateSuratService()

        template = service.create_template(
            actor=admin_user,
            kode="DOMISILI",
            nama="Surat Keterangan Domisili",
            deskripsi="Template domisili.",
            file_template=uploaded_docx_file,
            is_active=True,
        )

        assert template.id is not None
        assert template.kode == "DOMISILI"

    def test_warga_should_not_create_template(self, warga_user, uploaded_docx_file):
        service = TemplateSuratService()

        with pytest.raises(PermissionDeniedError):
            service.create_template(
                actor=warga_user,
                kode="DOMISILI",
                nama="Surat Keterangan Domisili",
                deskripsi="Template domisili.",
                file_template=uploaded_docx_file,
                is_active=True,
            )

    def test_should_list_active_templates(self, template_surat_aktif, template_surat_nonaktif):
        service = TemplateSuratService()

        templates = service.list_active_templates()

        assert template_surat_aktif in templates
        assert template_surat_nonaktif not in templates


@pytest.mark.django_db
class TestAjukanSurat:
    @patch("features.layanan_administrasi.services.audit_event")
    def test_warga_should_submit_surat_with_template_id(self, mock_audit, warga_user, template_surat_aktif):
        service = SuratService()

        surat = service.ajukan_surat(
            actor=warga_user,
            template_id=template_surat_aktif.id,
            keperluan="Untuk keperluan administrasi usaha.",
        )

        assert surat.id is not None
        assert surat.template_id == template_surat_aktif.id
        assert surat.jenis_surat == template_surat_aktif.kode
        mock_audit.assert_called_once()

    def test_should_reject_inactive_template(self, warga_user, template_surat_nonaktif):
        service = SuratService()

        with pytest.raises(Exception):
            service.ajukan_surat(
                actor=warga_user,
                template_id=template_surat_nonaktif.id,
                keperluan="Untuk keperluan administrasi usaha.",
            )

    def test_should_reject_missing_template_and_missing_jenis_surat(self, warga_user):
        service = SuratService()

        with pytest.raises(TemplateSuratNotFoundError):
            service.ajukan_surat(
                actor=warga_user,
                keperluan="Untuk keperluan administrasi usaha.",
            )

    def test_should_still_support_legacy_jenis_surat(self, warga_user):
        service = SuratService()

        surat = service.ajukan_surat(
            actor=warga_user,
            jenis_surat=JENIS_SKU,
            keperluan="Untuk keperluan administrasi usaha.",
        )

        assert surat.template_id is None
        assert surat.jenis_surat == JENIS_SKU


@pytest.mark.django_db
class TestProsesSuratAdvanced:
    def test_should_follow_valid_state_machine_flow(self, surat_setup):
        _, admin, service, surat = surat_setup

        service.proses_surat(admin, surat.id, STATUS_VERIFIED)
        service.proses_surat(admin, surat.id, STATUS_PROCESSED)
        updated = service.proses_surat(admin, surat.id, STATUS_DONE)

        assert updated.status == STATUS_DONE

    def test_should_reject_invalid_transition(self, surat_setup):
        _, admin, service, surat = surat_setup

        with pytest.raises(InvalidStatusTransitionError):
            service.proses_surat(admin, surat.id, STATUS_DONE)

    def test_should_require_rejection_reason(self, surat_setup):
        _, admin, service, surat = surat_setup

        service.proses_surat(admin, surat.id, STATUS_VERIFIED)

        with pytest.raises(RejectionReasonRequiredError):
            service.proses_surat(admin, surat.id, STATUS_REJECTED)

    def test_should_allow_rejection_with_reason(self, surat_setup):
        _, admin, service, surat = surat_setup

        service.proses_surat(admin, surat.id, STATUS_VERIFIED)

        updated = service.proses_surat(
            admin,
            surat.id,
            STATUS_REJECTED,
            rejection_reason="Dokumen tidak valid.",
        )

        assert updated.status == STATUS_REJECTED


@pytest.mark.django_db
class TestNomorSurat:
    @patch("features.layanan_administrasi.services.generate_nomor_surat")
    def test_should_generate_nomor_surat_if_not_provided(self, mock_nomor, surat_setup):
        mock_nomor.return_value = "AUTO-NOMOR"

        _, admin, service, surat = surat_setup

        service.proses_surat(admin, surat.id, STATUS_VERIFIED)
        service.proses_surat(admin, surat.id, STATUS_PROCESSED)
        updated = service.proses_surat(admin, surat.id, STATUS_DONE)

        assert updated.nomor_surat == "AUTO-NOMOR"

    def test_should_not_override_manual_nomor(self, surat_setup):
        _, admin, service, surat = surat_setup

        service.proses_surat(admin, surat.id, STATUS_VERIFIED)
        service.proses_surat(admin, surat.id, STATUS_PROCESSED)

        updated = service.proses_surat(
            admin,
            surat.id,
            STATUS_DONE,
            nomor_surat="MANUAL-123",
        )

        assert updated.nomor_surat == "MANUAL-123"


@pytest.mark.django_db
class TestDocxGeneration:
    def test_should_attach_docx_when_done_and_template_exists(self, surat_setup):
        _, admin, service, surat = surat_setup

        service.proses_surat(admin, surat.id, STATUS_VERIFIED)
        service.proses_surat(admin, surat.id, STATUS_PROCESSED)
        updated = service.proses_surat(admin, surat.id, STATUS_DONE)

        assert updated.docx_file
        assert updated.docx_file.name.endswith(".docx")

    def test_should_not_crash_when_template_missing(self, user_factory):
        warga = user_factory(role="WARGA")
        admin = user_factory(role="ADMIN", is_staff=True)
        service = SuratService(document_renderer=FakeDocumentRenderer())

        surat = service.repository.create_surat(
            pemohon_id=warga.id,
            jenis_surat="SKU",
            keperluan="Keperluan panjang untuk usaha.",
        )

        service.proses_surat(admin, surat.id, STATUS_VERIFIED)
        service.proses_surat(admin, surat.id, STATUS_PROCESSED)
        updated = service.proses_surat(admin, surat.id, STATUS_DONE)

        assert updated.status == STATUS_DONE


@pytest.mark.django_db
class TestAuditLogging:
    @patch("features.layanan_administrasi.services.audit_event")
    def test_should_log_event_when_submit(self, mock_audit, warga_user, template_surat_aktif):
        service = SuratService()

        surat = service.ajukan_surat(
            actor=warga_user,
            template_id=template_surat_aktif.id,
            keperluan="Untuk keperluan administrasi usaha.",
        )

        assert surat is not None
        mock_audit.assert_called_once()


@pytest.mark.django_db
class TestDataConsistency:
    def test_status_should_match_latest_history(self, surat_setup):
        _, admin, service, surat = surat_setup

        for status in [STATUS_VERIFIED, STATUS_PROCESSED, STATUS_DONE]:
            surat = service.proses_surat(admin, surat.id, status)

        last_history = surat.histori_status.first()

        assert last_history is not None
        assert surat.status == last_history.status_to
        assert surat.histori_status.count() == 4