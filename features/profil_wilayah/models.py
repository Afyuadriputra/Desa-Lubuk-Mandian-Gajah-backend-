# features/profil_wilayah/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from toolbox.storage.paths import perangkat_photo_upload_path

class WilayahDusun(models.Model):
    id = models.BigAutoField(primary_key=True)
    nama_dusun = models.CharField(max_length=100)
    kepala_dusun = models.CharField(max_length=150)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "wilayah_dusun"


class WilayahPerangkat(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    jabatan = models.CharField(max_length=100)
    foto = models.ImageField(upload_to=perangkat_photo_upload_path, blank=True, null=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "wilayah_perangkat"


class ProfilDesa(models.Model):
    """YAGNI: Tabel singleton untuk menyimpan Visi, Misi, dan Sejarah"""
    visi = models.TextField()
    misi = models.TextField()
    sejarah = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "profil_desa"