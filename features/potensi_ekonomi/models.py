# features/potensi_ekonomi/models.py

from django.db import models
from django.utils import timezone

from features.potensi_ekonomi.domain import VALID_KATEGORI
from toolbox.storage.paths import bumdes_media_upload_path


class BumdesUnitUsaha(models.Model):
    KATEGORI_CHOICES = [(k, k) for k in VALID_KATEGORI]

    id = models.BigAutoField(primary_key=True)
    nama_usaha = models.CharField(max_length=150)
    kategori = models.CharField(max_length=50, choices=KATEGORI_CHOICES)
    deskripsi = models.TextField()
    fasilitas = models.TextField(blank=True, null=True)  # Tambahan sesuai fitur PRD
    kontak_wa = models.CharField(max_length=20, blank=True, null=True)
    harga_tiket = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    foto_utama = models.ImageField(
        upload_to=bumdes_media_upload_path, 
        blank=True, 
        null=True
    )
    
    is_published = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bumdes_unit_usaha"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.nama_usaha} ({self.kategori})"