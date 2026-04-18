# backend/conftest.py (Taruh di sebelah manage.py)
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture(scope="function")
def admin_user(db):
    """Menimpa admin_user bawaan pytest agar valid dengan model Anda"""
    return User.objects.create_superuser(
        nik="9999999999999999",
        password="password123",
        nama_lengkap="Super Admin",
        role="SUPERADMIN"
    )

@pytest.fixture(scope="function")
def warga_user(db):
    """Data dummy untuk warga"""
    return User.objects.create_user(
        nik="1234123412341234",
        password="password123",
        nama_lengkap="Warga Biasa",
        role="WARGA"
    )