# features/auth_warga/domain.py

import re

ROLE_SUPERADMIN = "SUPERADMIN"
ROLE_ADMIN = "ADMIN"
ROLE_BUMDES = "BUMDES"
ROLE_WARGA = "WARGA"

VALID_ROLES = {
    ROLE_SUPERADMIN,
    ROLE_ADMIN,
    ROLE_BUMDES,
    ROLE_WARGA,
}

INTERNAL_ADMIN_ROLES = {
    ROLE_SUPERADMIN,
    ROLE_ADMIN,
    ROLE_BUMDES,
}


class AuthDomainError(Exception):
    """Base exception untuk domain auth."""


class InvalidNIKError(AuthDomainError):
    """NIK tidak valid."""


class InvalidRoleError(AuthDomainError):
    """Role tidak valid."""


class InactiveAccountError(AuthDomainError):
    """Akun nonaktif."""


class AuthenticationFailedError(AuthDomainError):
    """Login gagal."""


class DuplicateNIKError(AuthDomainError):
    """NIK sudah digunakan."""


def normalize_nik(nik: str | None) -> str:
    if nik is None:
        return ""
    return re.sub(r"\D", "", nik).strip()


def validate_nik(nik: str) -> None:
    if not nik:
        raise InvalidNIKError("NIK wajib diisi.")
    if len(nik) != 16:
        raise InvalidNIKError("NIK harus terdiri dari 16 digit.")
    if not nik.isdigit():
        raise InvalidNIKError("NIK hanya boleh berisi angka.")


def validate_role(role: str) -> None:
    if role not in VALID_ROLES:
        raise InvalidRoleError(f"Role '{role}' tidak valid.")


def ensure_account_is_active(is_active: bool) -> None:
    if not is_active:
        raise InactiveAccountError("Akun nonaktif dan tidak dapat login.")


def is_internal_admin_role(role: str) -> bool:
    return role in INTERNAL_ADMIN_ROLES