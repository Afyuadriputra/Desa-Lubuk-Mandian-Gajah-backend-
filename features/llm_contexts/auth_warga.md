# Feature Context: auth_warga

Generated at: 2026-04-17T14:51:50
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
- `views.py`
- `urls.py`

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

## File: `views.py`

```python
# features/auth_warga/views.py

import json

from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from features.auth_warga.domain import (
    AuthenticationFailedError,
    DuplicateNIKError,
    InactiveAccountError,
    InvalidNIKError,
    InvalidRoleError,
)
from features.auth_warga.services import (
    AuthService,
    PermissionDeniedError,
    UserNotFoundError,
)
from toolbox.security.auth import is_active_user

auth_service = AuthService()


def _parse_json_body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


@require_POST
def login_view(request):
    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Payload JSON tidak valid."}, status=400)

    nik = payload.get("nik", "")
    password = payload.get("password", "")

    if not nik or not password:
        return JsonResponse({"detail": "NIK dan kata sandi wajib diisi."}, status=400)

    try:
        result = auth_service.login_user(
            request=request,
            nik=nik,
            password=password,
        )
    except InvalidNIKError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except InactiveAccountError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)
    except AuthenticationFailedError as exc:
        return JsonResponse({"detail": str(exc)}, status=401)

    login(request, result.user)
    return JsonResponse(
        {
            "detail": result.message,
            "data": {
                "id": str(result.user.id),
                "nik": result.user.nik,
                "nama_lengkap": result.user.nama_lengkap,
                "role": result.user.role,
                "is_active": result.user.is_active,
            },
        },
        status=200,
    )


@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({"detail": "Logout berhasil."}, status=200)


@require_GET
def me_view(request):
    user = getattr(request, "user", None)
    if not is_active_user(user):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    return JsonResponse(
        {
            "data": {
                "id": str(user.id),
                "nik": user.nik,
                "nama_lengkap": user.nama_lengkap,
                "nomor_hp": user.nomor_hp,
                "role": user.role,
                "is_active": user.is_active,
            }
        },
        status=200,
    )


@require_POST
def create_warga_user_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Payload JSON tidak valid."}, status=400)

    try:
        user = auth_service.create_warga_account(
            actor=actor,
            nik=payload.get("nik", ""),
            password=payload.get("password", ""),
            nama_lengkap=payload.get("nama_lengkap", ""),
            nomor_hp=payload.get("nomor_hp"),
            is_active=payload.get("is_active", True),
        )
    except (InvalidNIKError, DuplicateNIKError, InvalidRoleError) as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)
    except ValueError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)

    return JsonResponse(
        {
            "detail": "Akun warga berhasil dibuat.",
            "data": {
                "id": str(user.id),
                "nik": user.nik,
                "nama_lengkap": user.nama_lengkap,
                "role": user.role,
                "is_active": user.is_active,
            },
        },
        status=201,
    )


@require_POST
def create_admin_user_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Payload JSON tidak valid."}, status=400)

    try:
        user = auth_service.create_admin_account(
            actor=actor,
            nik=payload.get("nik", ""),
            password=payload.get("password", ""),
            nama_lengkap=payload.get("nama_lengkap", ""),
            role=payload.get("role", ""),
            nomor_hp=payload.get("nomor_hp"),
            is_active=payload.get("is_active", True),
        )
    except (InvalidNIKError, DuplicateNIKError, InvalidRoleError) as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)
    except ValueError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)

    return JsonResponse(
        {
            "detail": "Akun admin berhasil dibuat.",
            "data": {
                "id": str(user.id),
                "nik": user.nik,
                "nama_lengkap": user.nama_lengkap,
                "role": user.role,
                "is_active": user.is_active,
            },
        },
        status=201,
    )


@require_POST
def activate_user_view(request, user_id):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    try:
        target_user = auth_service.activate_account(actor=actor, target_user_id=user_id)
    except UserNotFoundError as exc:
        return JsonResponse({"detail": str(exc)}, status=404)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)

    return JsonResponse(
        {
            "detail": "Akun berhasil diaktifkan.",
            "data": {
                "id": str(target_user.id),
                "nik": target_user.nik,
                "nama_lengkap": target_user.nama_lengkap,
                "role": target_user.role,
                "is_active": target_user.is_active,
            },
        },
        status=200,
    )


@require_POST
def deactivate_user_view(request, user_id):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    try:
        target_user = auth_service.deactivate_account(actor=actor, target_user_id=user_id)
    except UserNotFoundError as exc:
        return JsonResponse({"detail": str(exc)}, status=404)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)

    return JsonResponse(
        {
            "detail": "Akun berhasil dinonaktifkan.",
            "data": {
                "id": str(target_user.id),
                "nik": target_user.nik,
                "nama_lengkap": target_user.nama_lengkap,
                "role": target_user.role,
                "is_active": target_user.is_active,
            },
        },
        status=200,
    )
```

---

## File: `urls.py`

```python
# features/auth_warga/urls.py

from django.urls import path

from features.auth_warga.views import (
    activate_user_view,
    create_admin_user_view,
    create_warga_user_view,
    deactivate_user_view,
    login_view,
    logout_view,
    me_view,
)

urlpatterns = [
    path("login/", login_view, name="auth-login"),
    path("logout/", logout_view, name="auth-logout"),
    path("me/", me_view, name="auth-me"),
    path("users/warga/create/", create_warga_user_view, name="auth-create-warga-user"),
    path("users/admin/create/", create_admin_user_view, name="auth-create-admin-user"),
    path("users/<uuid:user_id>/activate/", activate_user_view, name="auth-activate-user"),
    path("users/<uuid:user_id>/deactivate/", deactivate_user_view, name="auth-deactivate-user"),
]
```

---
