import pytest

from features.layanan_administrasi.domain import (
    validate_jenis_surat,
    validate_keperluan,
    validate_status_transition,
    validate_rejection,
    InvalidJenisSuratError,
    InvalidKeperluanError,
    InvalidStatusTransitionError,
    RejectionReasonRequiredError,
    JENIS_SKU,
    STATUS_PENDING,
    STATUS_VERIFIED,
    STATUS_DONE,
    STATUS_REJECTED,
)


class TestJenisSuratValidation:
    def test_should_accept_valid_jenis_surat(self):
        """Validasi jenis surat yang benar harus lolos"""
        validate_jenis_surat(JENIS_SKU)

    def test_should_reject_invalid_jenis_surat(self):
        """Harus error jika jenis surat tidak valid"""
        with pytest.raises(InvalidJenisSuratError):
            validate_jenis_surat("SALAH")


class TestKeperluanValidation:
    def test_should_reject_empty_keperluan(self):
        """Harus error jika keperluan kosong"""
        with pytest.raises(InvalidKeperluanError):
            validate_keperluan("")

    def test_should_reject_short_keperluan(self):
        """Harus error jika keperluan terlalu pendek"""
        with pytest.raises(InvalidKeperluanError):
            validate_keperluan("pendek")

    def test_should_accept_valid_keperluan(self):
        """Keperluan valid harus lolos"""
        validate_keperluan("Mengurus keperluan administrasi desa")


class TestStatusTransition:
    def test_should_allow_valid_transition(self):
        """Transisi status valid harus lolos"""
        validate_status_transition(STATUS_PENDING, STATUS_VERIFIED)

    def test_should_reject_invalid_transition(self):
        """Transisi status tidak valid harus error"""
        with pytest.raises(InvalidStatusTransitionError):
            validate_status_transition(STATUS_DONE, STATUS_VERIFIED)


class TestRejectionValidation:
    def test_should_require_reason_when_rejected(self):
        """Status REJECTED wajib memiliki alasan"""
        with pytest.raises(RejectionReasonRequiredError):
            validate_rejection(STATUS_REJECTED, "")

    def test_should_pass_when_reason_provided(self):
        """Status REJECTED dengan alasan harus lolos"""
        validate_rejection(STATUS_REJECTED, "Dokumen tidak lengkap")