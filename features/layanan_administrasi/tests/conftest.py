# features/layanan_administrasi/tests/conftest.py

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from features.layanan_administrasi.models import TemplateSurat

User = get_user_model()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        nik="9999999999999999",
        password="password123",
        nama_lengkap="Super Admin Utama",
        role="SUPERADMIN",
    )


@pytest.fixture
def warga_user(db):
    return User.objects.create_user(
        nik="1234123412341234",
        password="password123",
        nama_lengkap="Warga Biasa",
        role="WARGA",
    )


@pytest.fixture
def uploaded_docx_file():
    return SimpleUploadedFile(
        "template-surat.docx",
        b"dummy-docx-content",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@pytest.fixture
def uploaded_txt_file():
    return SimpleUploadedFile(
        "template-surat.txt",
        b"not-a-docx",
        content_type="text/plain",
    )


@pytest.fixture
def template_surat_aktif(db, uploaded_docx_file):
    return TemplateSurat.objects.create(
        kode="SKU",
        nama="Surat Keterangan Usaha",
        deskripsi="Template aktif untuk surat usaha.",
        file_template=uploaded_docx_file,
        is_active=True,
    )


@pytest.fixture
def template_surat_nonaktif(db, uploaded_docx_file):
    return TemplateSurat.objects.create(
        kode="SKTM",
        nama="Surat Keterangan Tidak Mampu",
        deskripsi="Template tidak aktif.",
        file_template=uploaded_docx_file,
        is_active=False,
    )