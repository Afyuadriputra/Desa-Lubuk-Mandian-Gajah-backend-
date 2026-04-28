# features/layanan_administrasi/tests/test_domain.py

import pytest

from features.layanan_administrasi.domain import (
    JENIS_SKU,
    STATUS_DONE,
    STATUS_PENDING,
    STATUS_REJECTED,
    STATUS_VERIFIED,
    InvalidJenisSuratError,
    InvalidKeperluanError,
    InvalidStatusTransitionError,
    InvalidTemplateFileError,
    InvalidTemplateSuratError,
    RejectionReasonRequiredError,
    normalize_template_code,
    validate_jenis_surat,
    validate_keperluan,
    validate_rejection,
    validate_status_transition,
    validate_template_code,
    validate_template_file,
    validate_template_is_active,
    validate_template_name,
)


class TestJenisSuratValidation:
    def test_should_accept_valid_jenis_surat(self):
        validate_jenis_surat(JENIS_SKU)

    def test_should_reject_invalid_jenis_surat(self):
        with pytest.raises(InvalidJenisSuratError):
            validate_jenis_surat("SALAH")


class TestKeperluanValidation:
    def test_should_reject_empty_keperluan(self):
        with pytest.raises(InvalidKeperluanError):
            validate_keperluan("")

    def test_should_reject_short_keperluan(self):
        with pytest.raises(InvalidKeperluanError):
            validate_keperluan("pendek")

    def test_should_accept_valid_keperluan(self):
        validate_keperluan("Mengurus keperluan administrasi desa")


class TestStatusTransition:
    def test_should_allow_valid_transition(self):
        validate_status_transition(STATUS_PENDING, STATUS_VERIFIED)

    def test_should_reject_invalid_transition(self):
        with pytest.raises(InvalidStatusTransitionError):
            validate_status_transition(STATUS_DONE, STATUS_VERIFIED)


class TestRejectionValidation:
    def test_should_require_reason_when_rejected(self):
        with pytest.raises(RejectionReasonRequiredError):
            validate_rejection(STATUS_REJECTED, "")

    def test_should_pass_when_reason_provided(self):
        validate_rejection(STATUS_REJECTED, "Dokumen tidak lengkap")


class TestTemplateSuratValidation:
    def test_should_normalize_template_code(self):
        assert normalize_template_code(" sku ") == "SKU"

    def test_should_reject_empty_template_code(self):
        with pytest.raises(InvalidTemplateSuratError):
            validate_template_code("")

    def test_should_accept_valid_template_code(self):
        validate_template_code("DOMISILI")

    def test_should_reject_empty_template_name(self):
        with pytest.raises(InvalidTemplateSuratError):
            validate_template_name("")

    def test_should_accept_valid_template_name(self):
        validate_template_name("Surat Keterangan Domisili")

    def test_should_reject_non_docx_template_file(self):
        with pytest.raises(InvalidTemplateFileError):
            validate_template_file("template.pdf")

    def test_should_accept_docx_template_file(self):
        validate_template_file("template.docx")

    def test_should_reject_missing_template(self):
        with pytest.raises(InvalidTemplateSuratError):
            validate_template_is_active(None)

    def test_should_reject_inactive_template(self):
        class Template:
            is_active = False

        with pytest.raises(InvalidTemplateSuratError):
            validate_template_is_active(Template())

    def test_should_accept_active_template(self):
        class Template:
            is_active = True

        validate_template_is_active(Template())