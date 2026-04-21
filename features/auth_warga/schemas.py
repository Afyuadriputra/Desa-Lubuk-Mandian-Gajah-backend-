# features/auth_warga/schemas.py
from datetime import datetime
from ninja import Field, Schema
from uuid import UUID
from toolbox.security.sanitizers import SafePlainTextString

class LoginIn(Schema):
    nik: str
    password: str

class CsrfTokenOut(Schema):
    csrfToken: str = Field(..., alias="csrfToken")


class UserOut(Schema):
    id: UUID
    nik: str
    nama_lengkap: str
    nomor_hp: str | None = None
    role: str
    is_active: bool


class UserListQueryIn(Schema):
    q: str | None = Field(default=None)
    role: str | None = Field(default=None)
    is_active: bool | None = Field(default=None)


class GroupOut(Schema):
    id: int
    name: str


class PermissionOut(Schema):
    id: int
    app_label: str
    model: str
    codename: str
    name: str

    @staticmethod
    def resolve_app_label(obj):
        return obj.content_type.app_label

    @staticmethod
    def resolve_model(obj):
        return obj.content_type.model


class PermissionFlatOut(Schema):
    id: int
    app_label: str
    model: str
    codename: str
    name: str


class PermissionGroupOut(Schema):
    app_label: str
    model: str
    permissions: list[PermissionFlatOut]


class UserDetailOut(UserOut):
    is_staff: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None = None
    groups: list[GroupOut]
    user_permissions: list[PermissionOut] = Field(..., alias="user_permissions")


class UpdateUserIn(Schema):
    nama_lengkap: SafePlainTextString
    nomor_hp: str | None = None
    role: str
    is_active: bool
    is_staff: bool = False
    is_superuser: bool = False
    groups: list[int] = Field(default_factory=list)
    user_permissions: list[int] = Field(default_factory=list)

class CreateWargaIn(Schema):
    nik: str
    nama_lengkap: SafePlainTextString
    password: str
    nomor_hp: str = None


class CreateAdminIn(Schema):
    nik: str
    nama_lengkap: SafePlainTextString
    password: str
    role: str
    nomor_hp: str | None = None


class ActivationOut(Schema):
    id: UUID
    is_active: bool


class ChangePasswordIn(Schema):
    current_password: str
    new_password: str
    confirm_password: str


class ResetUserPasswordIn(Schema):
    new_password: str
    confirm_password: str
