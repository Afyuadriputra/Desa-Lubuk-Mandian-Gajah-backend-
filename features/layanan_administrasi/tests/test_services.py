import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model

from features.layanan_administrasi.services import SuratService
from features.layanan_administrasi.domain import (
    JENIS_SKU,
    STATUS_VERIFIED,
    STATUS_PROCESSED,
    STATUS_DONE,
    STATUS_REJECTED,
    InvalidStatusTransitionError,
    RejectionReasonRequiredError,
)

User = get_user_model()


# =========================
# 🔹 BASE FACTORY
# =========================
@pytest.fixture
def user_factory():
    counter = 1

    def create(role="WARGA", is_staff=False):
        nonlocal counter

        nik = str(counter).zfill(16)
        counter += 1

        return User.objects.create_user(
            nik=nik,
            password="pass",
            nama_lengkap=f"User {nik}",
            role=role,
            is_staff=is_staff,
        )

    return create


@pytest.fixture
def surat_setup(user_factory):
    warga = user_factory(role="WARGA")
    admin = user_factory(role="ADMIN", is_staff=True)

    service = SuratService()
    surat = service.repository.create_surat(
        warga.id, JENIS_SKU, "Keperluan panjang sekali"
    )

    return warga, admin, service, surat


# =========================
# 🔹 PROSES SURAT (ADVANCED)
# =========================
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
            rejection_reason="Tidak valid",
        )

        assert updated.status == STATUS_REJECTED


# =========================
# 🔹 NOMOR SURAT
# =========================
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


# =========================
# 🔹 PDF GENERATION
# =========================
@pytest.mark.django_db
class TestPDFGeneration:

    @patch("features.layanan_administrasi.services.generate_pdf_from_html")
    @patch("features.layanan_administrasi.services.render_surat_html")
    def test_should_attach_pdf_when_done(self, mock_render, mock_pdf, surat_setup):
        mock_render.return_value = "<html></html>"
        mock_pdf.return_value = b"PDF"

        _, admin, service, surat = surat_setup

        service.proses_surat(admin, surat.id, STATUS_VERIFIED)
        service.proses_surat(admin, surat.id, STATUS_PROCESSED)
        updated = service.proses_surat(admin, surat.id, STATUS_DONE)

        assert updated.pdf_file is not None

    @patch("features.layanan_administrasi.services.generate_pdf_from_html")
    @patch("features.layanan_administrasi.services.render_surat_html")
    def test_should_not_crash_when_pdf_fails(self, mock_render, mock_pdf, surat_setup):
        mock_render.return_value = "<html></html>"
        mock_pdf.side_effect = Exception("PDF ERROR")

        _, admin, service, surat = surat_setup

        service.proses_surat(admin, surat.id, STATUS_VERIFIED)
        service.proses_surat(admin, surat.id, STATUS_PROCESSED)

        updated = service.proses_surat(admin, surat.id, STATUS_DONE)

        assert updated.status == STATUS_DONE


# =========================
# 🔹 AUDIT LOG
# =========================
@pytest.mark.django_db
class TestAuditLogging:

    @patch("features.layanan_administrasi.services.audit_event")
    def test_should_log_event_when_submit(self, mock_audit, user_factory):

        warga = user_factory(role="WARGA")

        service = SuratService()
        surat = service.ajukan_surat(
            actor=warga,
            jenis_surat="SKU",
            keperluan="Untuk usaha",
        )

        assert surat is not None
        mock_audit.assert_called_once()


# =========================
# 🔹 DATA CONSISTENCY
# =========================
@pytest.mark.django_db
class TestDataConsistency:

    def test_status_should_match_latest_history(self, user_factory):

        warga = user_factory(role="WARGA")
        admin = user_factory(role="ADMIN", is_staff=True)

        service = SuratService()

        surat = service.ajukan_surat(
            actor=warga,
            jenis_surat="SKU",
            keperluan="Test konsistensi",
        )

        for status in [STATUS_VERIFIED, STATUS_PROCESSED, STATUS_DONE]:
            surat = service.proses_surat(admin, surat.id, status)

        last_history = surat.histori_status.first()

        assert last_history is not None
        assert surat.status == last_history.status_to
        assert surat.histori_status.count() == 4  # PENDING + 3 update