# features/layanan_administrasi/models.py

"""
Layer: Models

Tanggung jawab:
- Mendefinisikan struktur tabel database.
- Tidak berisi business logic berat.
- Tidak melakukan validasi flow bisnis.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from features.layanan_administrasi.domain import (
    STATUS_PENDING,
    VALID_STATUSES,
)
from toolbox.storage.paths import surat_pdf_upload_path


# ============================================================
# Upload Path Helpers
# ============================================================
# Catatan:
# - Fungsi kecil ini sengaja ditempatkan di models.py agar path upload
#   dekat dengan definisi field FileField.
# - Tetap KISS, tidak perlu membuat file baru hanya untuk path.
# ============================================================

def template_surat_upload_path(instance, filename: str) -> str:
    return f"template_surat/{instance.kode}/{filename}"


def surat_docx_upload_path(instance, filename: str) -> str:
    return f"surat/docx/{instance.id}/{filename}"


# ============================================================
# Template Surat
# ============================================================
# Fungsi:
# - Menyimpan file template Word (.docx) yang di-upload admin.
# - Template ini menjadi master surat yang akan diisi placeholder-nya.
# ============================================================

class TemplateSurat(models.Model):
    kode = models.CharField(
        max_length=50,
        unique=True,
        help_text="Kode unik template, contoh: SKU, SKTM, DOMISILI.",
    )
    nama = models.CharField(
        max_length=150,
        help_text="Nama template surat yang tampil ke admin/warga.",
    )
    deskripsi = models.TextField(
        blank=True,
        null=True,
        help_text="Deskripsi singkat kegunaan template surat.",
    )
    file_template = models.FileField(
        upload_to=template_surat_upload_path,
        help_text="File template surat dalam format .docx.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Template aktif bisa dipilih warga saat mengajukan surat.",
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "template_surat"
        ordering = ["nama"]

    def __str__(self):
        return f"{self.kode} - {self.nama}"


# ============================================================
# Layanan Surat
# ============================================================
# Fungsi:
# - Menyimpan pengajuan surat dari warga.
# - Menyimpan hasil generate surat, baik PDF lama maupun DOCX baru.
# ============================================================

class LayananSurat(models.Model):
    STATUS_CHOICES = [(s, s) for s in VALID_STATUSES]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    pemohon = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="surat_diajukan",
    )

    # ------------------------------------------------------------
    # Template dinamis
    # ------------------------------------------------------------
    # template:
    # - Relasi ke TemplateSurat.
    # - Dibuat nullable agar data lama yang hanya punya jenis_surat
    #   tetap aman saat migrasi.
    #
    # jenis_surat:
    # - Tetap dipertahankan sebagai snapshot kode surat.
    # - Tidak memakai choices lagi agar bisa mengikuti template dinamis.
    # ------------------------------------------------------------
    template = models.ForeignKey(
        TemplateSurat,
        on_delete=models.PROTECT,
        related_name="layanan_surat",
        blank=True,
        null=True,
    )
    jenis_surat = models.CharField(max_length=50)

    keperluan = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    nomor_surat = models.CharField(max_length=100, blank=True, null=True)

    # ------------------------------------------------------------
    # File hasil surat
    # ------------------------------------------------------------
    # pdf_file:
    # - Dipertahankan untuk fitur lama.
    #
    # docx_file:
    # - File hasil generate dari template Word.
    # - Ini yang dibutuhkan untuk flow template .docx.
    # ------------------------------------------------------------
    pdf_file = models.FileField(
        upload_to=surat_pdf_upload_path,
        blank=True,
        null=True,
    )
    docx_file = models.FileField(
        upload_to=surat_docx_upload_path,
        blank=True,
        null=True,
    )

    rejection_reason = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "layanan_surat"
        ordering = ["-created_at"]

    def __str__(self):
        pemohon_nama = getattr(self.pemohon, "nama_lengkap", self.pemohon_id)
        return f"{self.jenis_surat} - {pemohon_nama} ({self.status})"


# ============================================================
# Histori Status Surat
# ============================================================
# Fungsi:
# - Mencatat perubahan status surat.
# - Tidak menyimpan logic transisi status. Logic tetap di domain.py.
# ============================================================

class LayananSuratStatusHistory(models.Model):
    surat = models.ForeignKey(
        LayananSurat,
        on_delete=models.CASCADE,
        related_name="histori_status",
    )
    status_from = models.CharField(max_length=20, blank=True, null=True)
    status_to = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        db_table = "layanan_surat_status_history"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.surat.id} : {self.status_from} -> {self.status_to}"