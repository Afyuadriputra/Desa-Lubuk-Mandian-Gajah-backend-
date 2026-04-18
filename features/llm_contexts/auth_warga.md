# Feature Context: auth_warga

Generated at: 2026-04-18T23:18:05
Feature path: `D:\Kuliah\joki\radit\desa\backend\features\auth_warga`

Dokumen ini berisi layer penting untuk konteks LLM.
Folder `tests`, `migrations`, `logs`, dan file non-konteks tidak disertakan.

## Included Layers

- `apps.py`
- `models.py`
- `domain.py`
- `repositories.py`
- `services.py`
- `permissions.py`
- `schemas.py`
- `api.py`

---

## File: `apps.py`

```python
# features/auth_warga/apps.py

from django.apps import AppConfig


class AuthWargaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "features.auth_warga"
```

---

## File: `models.py`

```python
# features/auth_warga/models.py

import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from features.auth_warga.domain import (
    ROLE_ADMIN,
    ROLE_BUMDES,
    ROLE_SUPERADMIN,
    ROLE_WARGA,
    normalize_nik,
    validate_nik,
    validate_role,
)


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(
        self,
        nik: str,
        password: str,
        nama_lengkap: str,
        role: str = ROLE_WARGA,
        **extra_fields,
    ):
        if not nik:
            raise ValueError("NIK wajib diisi.")
        if not password:
            raise ValueError("Password wajib diisi.")
        if not nama_lengkap:
            raise ValueError("Nama lengkap wajib diisi.")

        nik = normalize_nik(nik)
        validate_nik(nik)
        validate_role(role)

        user = self.model(
            nik=nik,
            nama_lengkap=nama_lengkap.strip(),
            role=role,
            **extra_fields,
        )
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_user(
        self,
        nik: str,
        password: str,
        nama_lengkap: str,
        role: str = ROLE_WARGA,
        **extra_fields,
    ):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(
            nik=nik,
            password=password,
            nama_lengkap=nama_lengkap,
            role=role,
            **extra_fields,
        )

    def create_superuser(
        self,
        nik: str,
        password: str,
        nama_lengkap: str,
        **extra_fields,
    ):
        extra_fields.setdefault("role", ROLE_SUPERADMIN)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields["is_staff"] is not True:
            raise ValueError("Superuser harus memiliki is_staff=True.")
        if extra_fields["is_superuser"] is not True:
            raise ValueError("Superuser harus memiliki is_superuser=True.")

        role = extra_fields.pop("role")
        validate_role(role)

        return self._create_user(
            nik=nik,
            password=password,
            nama_lengkap=nama_lengkap,
            role=role,
            **extra_fields,
        )


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        (ROLE_SUPERADMIN, "Super Admin"),
        (ROLE_ADMIN, "Admin Desa"),
        (ROLE_BUMDES, "Admin BUMDes"),
        (ROLE_WARGA, "Warga"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nik = models.CharField(max_length=16, unique=True, db_index=True)
    nama_lengkap = models.CharField(max_length=150)
    nomor_hp = models.CharField(max_length=20, blank=True, null=True)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_WARGA,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "nik"
    REQUIRED_FIELDS = ["nama_lengkap"]

    objects = CustomUserManager()

    class Meta:
        db_table = "users_customuser"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        self.nik = normalize_nik(self.nik)
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        self.nik = normalize_nik(self.nik)
        validate_nik(self.nik)
        validate_role(self.role)

    def __str__(self) -> str:
        return f"{self.nama_lengkap} ({self.nik})"
```

---

## File: `domain.py`

```python
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
```

---

## File: `repositories.py`

```python
# features/auth_warga/repositories.py

from django.db.models import QuerySet

from features.auth_warga.models import CustomUser


class UserRepository:
    def get_by_id(self, user_id) -> CustomUser | None:
        return CustomUser.objects.filter(id=user_id).first()

    def get_by_nik(self, nik: str) -> CustomUser | None:
        return CustomUser.objects.filter(nik=nik).first()

    def exists_by_nik(self, nik: str) -> bool:
        return CustomUser.objects.filter(nik=nik).exists()

    def list_all(self) -> QuerySet[CustomUser]:
        return CustomUser.objects.all()

    def list_by_role(self, role: str) -> QuerySet[CustomUser]:
        return CustomUser.objects.filter(role=role)

    def create_user(
        self,
        nik: str,
        password: str,
        nama_lengkap: str,
        role: str,
        nomor_hp: str | None = None,
        is_active: bool = True,
        is_staff: bool = False,
    ) -> CustomUser:
        return CustomUser.objects.create_user(
            nik=nik,
            password=password,
            nama_lengkap=nama_lengkap,
            role=role,
            nomor_hp=nomor_hp,
            is_active=is_active,
            is_staff=is_staff,
        )

    def save(self, user: CustomUser) -> CustomUser:
        user.save()
        return user

    def activate(self, user: CustomUser) -> CustomUser:
        user.is_active = True
        user.save(update_fields=["is_active", "updated_at"])
        return user

    def deactivate(self, user: CustomUser) -> CustomUser:
        user.is_active = False
        user.save(update_fields=["is_active", "updated_at"])
        return user
```

---

## File: `services.py`

```python
# features/auth_warga/services.py

from dataclasses import dataclass
from typing import cast

from django.contrib.auth import authenticate
from django.http import HttpRequest

from features.auth_warga.domain import (
    AuthenticationFailedError,
    DuplicateNIKError,
    InvalidRoleError,
    InactiveAccountError,
    ROLE_ADMIN,
    ROLE_BUMDES,
    ROLE_SUPERADMIN,
    ROLE_WARGA,
    ensure_account_is_active,
    normalize_nik,
    validate_nik,
    validate_role,
)
from features.auth_warga.models import CustomUser
from features.auth_warga.permissions import (
    can_activate_user,
    can_create_admin_user,
    can_create_warga_user,
    can_deactivate_user,
)
from features.auth_warga.repositories import UserRepository
from toolbox.logging import audit_event, get_logger


class PermissionDeniedError(Exception):
    """Permission denied pada service layer."""


class UserNotFoundError(Exception):
    """User tidak ditemukan."""


@dataclass
class LoginResult:
    user: CustomUser
    message: str = "Login berhasil."


class AuthService:
    def __init__(self, user_repository: UserRepository | None = None):
        self.user_repository = user_repository or UserRepository()
        self.logger = get_logger("features.auth_warga.services")

    def login_user(self, request: HttpRequest, nik: str, password: str) -> LoginResult:
        normalized_nik = normalize_nik(nik)

        # Sengaja tetap validasi format NIK.
        # Kalau format salah -> 400 dari view.
        validate_nik(normalized_nik)

        user = self.user_repository.get_by_nik(normalized_nik)
        if not user:
            audit_event(
                action="AUTH_LOGIN_FAILED",
                actor_id=None,
                actor_role=None,
                target="users_customuser",
                target_id=None,
                metadata={"reason": "user_not_found"},
            )
            raise AuthenticationFailedError("NIK atau kata sandi salah.")

        try:
            ensure_account_is_active(user.is_active)
        except InactiveAccountError:
            audit_event(
                action="AUTH_LOGIN_BLOCKED_INACTIVE",
                actor_id=user.id,
                actor_role=user.role,
                target="users_customuser",
                target_id=user.id,
                metadata={},
            )
            raise

        authenticated_user = cast(
            CustomUser | None,
            authenticate(
                request=request,
                username=normalized_nik,
                password=password,
            ),
        )

        if not authenticated_user:
            audit_event(
                action="AUTH_LOGIN_FAILED",
                actor_id=user.id,
                actor_role=user.role,
                target="users_customuser",
                target_id=user.id,
                metadata={"reason": "invalid_password"},
            )
            raise AuthenticationFailedError("NIK atau kata sandi salah.")

        audit_event(
            action="AUTH_LOGIN_SUCCESS",
            actor_id=authenticated_user.id,
            actor_role=authenticated_user.role,
            target="users_customuser",
            target_id=authenticated_user.id,
            metadata={},
        )

        self.logger.info(
            "Login berhasil untuk user_id={user_id}",
            user_id=authenticated_user.id,
        )
        return LoginResult(user=authenticated_user)

    def create_warga_account(
        self,
        actor: CustomUser,
        nik: str,
        password: str,
        nama_lengkap: str,
        nomor_hp: str | None = None,
        is_active: bool = True,
    ) -> CustomUser:
        if not can_create_warga_user(actor):
            raise PermissionDeniedError("Anda tidak memiliki izin untuk membuat akun warga.")

        normalized_nik = normalize_nik(nik)
        validate_nik(normalized_nik)

        if self.user_repository.exists_by_nik(normalized_nik):
            raise DuplicateNIKError("NIK sudah terdaftar.")

        created_user = self.user_repository.create_user(
            nik=normalized_nik,
            password=password,
            nama_lengkap=nama_lengkap,
            nomor_hp=nomor_hp,
            role=ROLE_WARGA,
            is_active=is_active,
            is_staff=False,
        )

        audit_event(
            action="AUTH_WARGA_ACCOUNT_CREATED",
            actor_id=actor.id,
            actor_role=actor.role,
            target="users_customuser",
            target_id=created_user.id,
            metadata={"target_role": created_user.role},
        )

        return created_user

    def create_admin_account(
        self,
        actor: CustomUser,
        nik: str,
        password: str,
        nama_lengkap: str,
        role: str,
        nomor_hp: str | None = None,
        is_active: bool = True,
    ) -> CustomUser:
        if not can_create_admin_user(actor):
            raise PermissionDeniedError("Anda tidak memiliki izin untuk membuat akun admin.")

        validate_role(role)
        if role not in {ROLE_ADMIN, ROLE_BUMDES, ROLE_SUPERADMIN}:
            raise InvalidRoleError("Role admin yang diizinkan hanya SUPERADMIN, ADMIN, atau BUMDES.")

        normalized_nik = normalize_nik(nik)
        validate_nik(normalized_nik)

        if self.user_repository.exists_by_nik(normalized_nik):
            raise DuplicateNIKError("NIK sudah terdaftar.")

        created_user = self.user_repository.create_user(
            nik=normalized_nik,
            password=password,
            nama_lengkap=nama_lengkap,
            nomor_hp=nomor_hp,
            role=role,
            is_active=is_active,
            is_staff=True,
        )

        audit_event(
            action="AUTH_ADMIN_ACCOUNT_CREATED",
            actor_id=actor.id,
            actor_role=actor.role,
            target="users_customuser",
            target_id=created_user.id,
            metadata={"target_role": created_user.role},
        )

        return created_user

    def activate_account(self, actor: CustomUser, target_user_id) -> CustomUser:
        target_user = self.user_repository.get_by_id(target_user_id)
        if not target_user:
            raise UserNotFoundError("User tidak ditemukan.")

        if not can_activate_user(actor, target_user):
            raise PermissionDeniedError("Anda tidak memiliki izin untuk mengaktifkan akun ini.")

        if target_user.is_active:
            return target_user

        updated_user = self.user_repository.activate(target_user)

        audit_event(
            action="AUTH_ACCOUNT_ACTIVATED",
            actor_id=actor.id,
            actor_role=actor.role,
            target="users_customuser",
            target_id=updated_user.id,
            metadata={"target_role": updated_user.role},
        )

        self.logger.info(
            "Akun diaktifkan actor_id={actor_id} target_user_id={target_user_id}",
            actor_id=actor.id,
            target_user_id=updated_user.id,
        )
        return updated_user

    def deactivate_account(self, actor: CustomUser, target_user_id) -> CustomUser:
        target_user = self.user_repository.get_by_id(target_user_id)
        if not target_user:
            raise UserNotFoundError("User tidak ditemukan.")

        if not can_deactivate_user(actor, target_user):
            raise PermissionDeniedError("Anda tidak memiliki izin untuk menonaktifkan akun ini.")

        if not target_user.is_active:
            return target_user

        updated_user = self.user_repository.deactivate(target_user)

        audit_event(
            action="AUTH_ACCOUNT_DEACTIVATED",
            actor_id=actor.id,
            actor_role=actor.role,
            target="users_customuser",
            target_id=updated_user.id,
            metadata={"target_role": updated_user.role},
        )

        self.logger.info(
            "Akun dinonaktifkan actor_id={actor_id} target_user_id={target_user_id}",
            actor_id=actor.id,
            target_user_id=updated_user.id,
        )
        return updated_user
```

---

## File: `permissions.py`

```python
# features/auth_warga/permissions.py

from features.auth_warga.domain import (
    ROLE_ADMIN,
    ROLE_BUMDES,
    ROLE_SUPERADMIN,
)
from toolbox.security.auth import is_active_user
from toolbox.security.permissions import (
    can_manage_admin_accounts,
    can_manage_warga_accounts,
)


ADMIN_SIDE_ROLES = {
    ROLE_SUPERADMIN,
    ROLE_ADMIN,
    ROLE_BUMDES,
}


def can_view_self(actor, target_user) -> bool:
    return is_active_user(actor) and str(actor.id) == str(target_user.id)


def can_activate_user(actor, target_user) -> bool:
    if target_user.role in ADMIN_SIDE_ROLES:
        return can_manage_admin_accounts(actor)
    return can_manage_warga_accounts(actor)


def can_deactivate_user(actor, target_user) -> bool:
    if str(actor.id) == str(target_user.id):
        return False

    if target_user.role in ADMIN_SIDE_ROLES:
        return can_manage_admin_accounts(actor)
    return can_manage_warga_accounts(actor)


def can_create_admin_user(actor) -> bool:
    return can_manage_admin_accounts(actor)


def can_create_warga_user(actor) -> bool:
    return can_manage_warga_accounts(actor)
```

---

## File: `schemas.py`

```python
# features/auth_warga/schemas.py
from ninja import Schema
from uuid import UUID
from toolbox.security.sanitizers import SafePlainTextString

class LoginIn(Schema):
    nik: str
    password: str

class UserOut(Schema):
    id: UUID
    nik: str
    nama_lengkap: str
    role: str
    is_active: bool

class CreateWargaIn(Schema):
    nik: str
    nama_lengkap: SafePlainTextString
    password: str
    nomor_hp: str = None
```

---

## File: `api.py`

```python
# features/auth_warga/api.py
from django.contrib.auth import login, logout
from ninja import Router
from .schemas import LoginIn, UserOut, CreateWargaIn
from .services import AuthService
from toolbox.api.auth import AuthActiveUser, AuthAdminOnly

router = Router(tags=["Autentikasi & Akun"])
auth_service = AuthService()

@router.post("/login", response={200: UserOut})
def login_api(request, payload: LoginIn):
    result = auth_service.login_user(request, payload.nik, payload.password)
    login(request, result.user)
    return result.user

@router.post("/logout", auth=AuthActiveUser)
def logout_api(request):
    logout(request)
    return {"detail": "Logout berhasil."}

@router.get("/me", auth=AuthActiveUser, response=UserOut)
def me_api(request):
    return request.user

@router.post("/users/warga/create", auth=AuthAdminOnly, response={201: UserOut})
def create_warga_api(request, payload: CreateWargaIn):
    user = auth_service.create_warga_account(
        actor=request.user,
        **payload.dict()
    )
    return 201, user
```

---
