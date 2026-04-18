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