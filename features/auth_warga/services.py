# features/auth_warga/services.py

from dataclasses import dataclass
from typing import cast

from django.contrib.auth.models import Group, Permission
from django.contrib.auth import authenticate
from django.http import HttpRequest

from features.auth_warga.domain import (
    AuthenticationFailedError,
    DuplicateNIKError,
    InvalidRoleError,
    InvalidPasswordChangeError,
    InactiveAccountError,
    ROLE_ADMIN,
    ROLE_BUMDES,
    ROLE_SUPERADMIN,
    ROLE_WARGA,
    ensure_account_is_active,
    normalize_nik,
    validate_nik,
    validate_password_change,
    validate_role,
)
from features.auth_warga.models import CustomUser
from features.auth_warga.permissions import (
    can_assign_groups_and_permissions,
    can_activate_user,
    can_create_admin_user,
    can_create_warga_user,
    can_deactivate_user,
    can_edit_user,
    can_list_users,
    can_view_user_detail,
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

    def list_users(
        self,
        actor: CustomUser,
        q: str | None = None,
        role: str | None = None,
        is_active: bool | None = None,
    ) -> list[CustomUser]:
        if not can_list_users(actor):
            raise PermissionDeniedError("Anda tidak memiliki izin untuk melihat daftar akun.")

        return list(
            self.user_repository.list_users(
                q=q,
                role=role,
                is_active=is_active,
            )
        )

    def get_user_detail(self, actor: CustomUser, target_user_id) -> CustomUser:
        target_user = self.user_repository.get_detail_by_id(target_user_id)
        if not target_user:
            raise UserNotFoundError("User tidak ditemukan.")

        if not can_view_user_detail(actor, target_user):
            raise PermissionDeniedError("Anda tidak memiliki izin untuk melihat detail akun ini.")

        return target_user

    def list_groups(self, actor: CustomUser) -> list[Group]:
        if not can_list_users(actor):
            raise PermissionDeniedError("Anda tidak memiliki izin untuk melihat grup.")
        return list(self.user_repository.list_groups())

    def list_permissions(self, actor: CustomUser) -> list[Permission]:
        if not can_list_users(actor):
            raise PermissionDeniedError("Anda tidak memiliki izin untuk melihat permission.")
        return list(self.user_repository.list_permissions())

    def update_user(
        self,
        actor: CustomUser,
        target_user_id,
        *,
        nama_lengkap: str,
        nomor_hp: str | None,
        role: str,
        is_active: bool,
        is_staff: bool,
        is_superuser: bool,
        groups: list[int],
        user_permissions: list[int],
    ) -> CustomUser:
        target_user = self.user_repository.get_detail_by_id(target_user_id)
        if not target_user:
            raise UserNotFoundError("User tidak ditemukan.")

        if not can_edit_user(actor, target_user):
            raise PermissionDeniedError("Anda tidak memiliki izin untuk mengubah akun ini.")

        can_manage_admin = can_assign_groups_and_permissions(actor)

        if not can_manage_admin:
            if target_user.role != ROLE_WARGA:
                raise PermissionDeniedError("Anda tidak memiliki izin untuk mengubah akun admin.")
            if role != ROLE_WARGA:
                raise PermissionDeniedError("Anda tidak memiliki izin mengubah role akun warga.")
            if is_staff or is_superuser or groups or user_permissions:
                raise PermissionDeniedError("Anda tidak memiliki izin mengubah permission akun.")

        validate_role(role)

        target_user.nama_lengkap = nama_lengkap
        target_user.nomor_hp = nomor_hp
        target_user.role = role
        target_user.is_active = is_active

        if can_manage_admin:
            target_user.is_staff = is_staff
            target_user.is_superuser = is_superuser

        updated_user = self.user_repository.save(target_user)

        if can_manage_admin:
            selected_groups = list(self.user_repository.list_groups().filter(id__in=groups))
            selected_permissions = list(self.user_repository.list_permissions().filter(id__in=user_permissions))
            self.user_repository.set_groups(updated_user, selected_groups)
            self.user_repository.set_user_permissions(updated_user, selected_permissions)

        audit_event(
            action="AUTH_ACCOUNT_UPDATED",
            actor_id=actor.id,
            actor_role=actor.role,
            target="users_customuser",
            target_id=updated_user.id,
            metadata={
                "target_role": updated_user.role,
                "groups_count": len(groups) if can_manage_admin else updated_user.groups.count(),
                "permissions_count": len(user_permissions) if can_manage_admin else updated_user.user_permissions.count(),
            },
        )

        return self.user_repository.get_detail_by_id(updated_user.id) or updated_user

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

    def change_password(
        self,
        actor: CustomUser,
        current_password: str,
        new_password: str,
        confirm_password: str,
    ) -> CustomUser:
        validate_password_change(current_password, new_password, confirm_password)

        if not actor.check_password(current_password):
            raise InvalidPasswordChangeError("Password lama tidak sesuai.")

        updated_user = self.user_repository.update_password(actor, new_password)

        audit_event(
            action="AUTH_PASSWORD_CHANGED",
            actor_id=actor.id,
            actor_role=actor.role,
            target="users_customuser",
            target_id=updated_user.id,
            metadata={},
        )

        self.logger.info("Password diubah untuk user_id={user_id}", user_id=updated_user.id)
        return updated_user
