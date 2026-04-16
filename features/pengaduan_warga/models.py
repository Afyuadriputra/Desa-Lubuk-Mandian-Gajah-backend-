# features/pengaduan_warga/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone

from features.pengaduan_warga.domain import STATUS_OPEN, VALID_STATUSES
from toolbox.storage.paths import pengaduan_bukti_upload_path


class LayananPengaduan(models.Model):
    STATUS_CHOICES = [(s, s) for s in VALID_STATUSES]

    # PRD meminta id SERIAL (integer auto-increment)
    id = models.BigAutoField(primary_key=True)
    pelapor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="pengaduan_dibuat"
    )
    kategori = models.CharField(max_length=50)
    judul = models.CharField(max_length=150)
    deskripsi = models.TextField()
    
    foto_bukti = models.ImageField(
        upload_to=pengaduan_bukti_upload_path, 
        blank=True, 
        null=True
    )
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default=STATUS_OPEN
    )
    
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "layanan_pengaduan"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.status}] {self.judul[:20]}... - {self.pelapor.nama_lengkap}"


class LayananPengaduanHistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    pengaduan = models.ForeignKey(
        LayananPengaduan, 
        on_delete=models.CASCADE, 
        related_name="histori_tindak_lanjut"
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
        db_table = "layanan_pengaduan_history"
        ordering = ["-created_at"]