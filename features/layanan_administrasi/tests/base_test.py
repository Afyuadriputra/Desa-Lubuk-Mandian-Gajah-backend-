# features/layanan_administrasi/tests/base_test.py

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def warga():
    return User.objects.create_user(
        nik="2222222222222222",
        password="password123",
        nama_lengkap="Warga",
        role="WARGA",
    )


@pytest.fixture
def admin():
    return User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="Admin",
        role="ADMIN",
        is_staff=True,
    )