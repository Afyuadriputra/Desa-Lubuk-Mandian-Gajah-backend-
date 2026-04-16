# features/auth_warga/tests/test_domain.py

import pytest

from features.auth_warga.domain import (
    InactiveAccountError,
    InvalidNIKError,
    InvalidRoleError,
    ROLE_ADMIN,
    ROLE_BUMDES,
    ROLE_SUPERADMIN,
    ROLE_WARGA,
    ensure_account_is_active,
    is_internal_admin_role,
    normalize_nik,
    validate_nik,
    validate_role,
)


class TestNormalizeNIK:

    def test_should_remove_non_digit_characters_from_nik(self):
        """NIK harus hanya berisi angka setelah dinormalisasi"""
        result = normalize_nik("12 34-56abc78901234")
        assert result == "12345678901234"


class TestValidateNIK:

    def test_should_pass_when_nik_is_valid_16_digits(self):
        """Validasi berhasil jika NIK terdiri dari 16 digit"""
        validate_nik("1234567890123456")

    def test_should_raise_error_when_nik_length_is_invalid(self):
        """Harus error jika panjang NIK tidak 16 digit"""
        with pytest.raises(InvalidNIKError):
            validate_nik("123")


class TestAccountStatus:

    def test_should_raise_error_when_account_is_inactive(self):
        """Harus error jika akun tidak aktif"""
        with pytest.raises(InactiveAccountError):
            ensure_account_is_active(False)


class TestValidateRole:

    def test_should_pass_for_all_valid_roles(self):
        """Semua role valid harus lolos validasi"""
        validate_role(ROLE_SUPERADMIN)
        validate_role(ROLE_ADMIN)
        validate_role(ROLE_BUMDES)
        validate_role(ROLE_WARGA)

    def test_should_raise_error_for_invalid_role(self):
        """Harus error jika role tidak termasuk role valid"""
        with pytest.raises(InvalidRoleError):
            validate_role("KEPALA_SEKSI")


class TestInternalAdminRole:

    def test_should_return_true_for_internal_admin_roles(self):
        """SUPERADMIN, ADMIN, BUMDES termasuk internal admin"""
        assert is_internal_admin_role(ROLE_SUPERADMIN) is True
        assert is_internal_admin_role(ROLE_ADMIN) is True
        assert is_internal_admin_role(ROLE_BUMDES) is True

    def test_should_return_false_for_warga_role(self):
        """WARGA bukan internal admin"""
        assert is_internal_admin_role(ROLE_WARGA) is False