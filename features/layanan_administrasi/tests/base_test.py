# features/layanan_administrasi/tests/base_test.py

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from features.layanan_administrasi.models import TemplateSurat

User = get_user_model()


@pytest.fixture
def warga(db):
    return User.objects.create_user(
        nik="2222222222222222",
        password="password123",
        nama_lengkap="Warga",
        role="WARGA",
    )


@pytest.fixture
def admin(db):
    return User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="Admin",
        role="ADMIN",
        is_staff=True,
    )


@pytest.fixture
def uploaded_docx_file():
    """File dummy untuk test upload. Tidak dipakai render asli."""
    return SimpleUploadedFile(
        "template-surat.docx",
        b"dummy-docx-content",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@pytest.fixture
def template_surat_aktif(db, uploaded_docx_file):
    return TemplateSurat.objects.create(
        kode="SKU",
        nama="Surat Keterangan Usaha",
        deskripsi="Template surat untuk keterangan usaha warga.",
        file_template=uploaded_docx_file,
        is_active=True,
    )


@pytest.fixture
def template_surat_nonaktif(db, uploaded_docx_file):
    return TemplateSurat.objects.create(
        kode="SKTM",
        nama="Surat Keterangan Tidak Mampu",
        deskripsi="Template surat nonaktif.",
        file_template=uploaded_docx_file,
        is_active=False,
    )