# features/layanan_administrasi/models.py

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

from features.layanan_administrasi.domain import (
    STATUS_PENDING,
    VALID_JENIS_SURAT,
    VALID_STATUSES,
)
from toolbox.storage.paths import surat_pdf_upload_path


class LayananSurat(models.Model):
    JENIS_CHOICES = [(j, j) for j in VALID_JENIS_SURAT]
    STATUS_CHOICES = [(s, s) for s in VALID_STATUSES]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pemohon = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="surat_diajukan"
    )
    jenis_surat = models.CharField(max_length=50, choices=JENIS_CHOICES)
    keperluan = models.TextField()
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default=STATUS_PENDING
    )
    nomor_surat = models.CharField(max_length=100, blank=True, null=True)
    pdf_file = models.FileField(upload_to=surat_pdf_upload_path, blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "layanan_surat"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.jenis_surat} - {self.pemohon.nama_lengkap} ({self.status})"


class LayananSuratStatusHistory(models.Model):
    surat = models.ForeignKey(
        LayananSurat, 
        on_delete=models.CASCADE, 
        related_name="histori_status"
    )
    status_from = models.CharField(max_length=20, blank=True, null=True)
    status_to = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        db_table = "layanan_surat_status_history"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.surat.id} : {self.status_from} -> {self.status_to}"