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


def test_normalize_nik_keeps_digits_only():
    assert normalize_nik("12 34-56abc78901234") == "12345678901234"


def test_validate_nik_success():
    validate_nik("1234567890123456")


def test_validate_nik_invalid_length():
    with pytest.raises(InvalidNIKError):
        validate_nik("123")


def test_ensure_account_is_active_raises_when_inactive():
    with pytest.raises(InactiveAccountError):
        ensure_account_is_active(False)


def test_validate_role_success_for_all_valid_roles():
    validate_role(ROLE_SUPERADMIN)
    validate_role(ROLE_ADMIN)
    validate_role(ROLE_BUMDES)
    validate_role(ROLE_WARGA)


def test_validate_role_invalid_role():
    with pytest.raises(InvalidRoleError):
        validate_role("KEPALA_SEKSI")


def test_is_internal_admin_role_returns_true_for_admin_roles():
    assert is_internal_admin_role(ROLE_SUPERADMIN) is True
    assert is_internal_admin_role(ROLE_ADMIN) is True
    assert is_internal_admin_role(ROLE_BUMDES) is True


def test_is_internal_admin_role_returns_false_for_warga():
    assert is_internal_admin_role(ROLE_WARGA) is False