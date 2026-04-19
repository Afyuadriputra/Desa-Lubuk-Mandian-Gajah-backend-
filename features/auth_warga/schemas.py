# features/auth_warga/schemas.py
from ninja import Field, Schema
from uuid import UUID
from toolbox.security.sanitizers import SafePlainTextString

class LoginIn(Schema):
    nik: str
    password: str

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
