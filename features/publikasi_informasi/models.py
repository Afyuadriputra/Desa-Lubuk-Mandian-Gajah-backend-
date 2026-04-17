from django.db import models

# Create your models here.
# features/publikasi_informasi/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify

from features.publikasi_informasi.domain import VALID_STATUS, VALID_JENIS


class Publikasi(models.Model):
    STATUS_CHOICES = [(s, s) for s in VALID_STATUS]
    JENIS_CHOICES = [(j, j) for j in VALID_JENIS]

    id = models.BigAutoField(primary_key=True)
    judul = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    konten_html = models.TextField()
    jenis = models.CharField(max_length=20, choices=JENIS_CHOICES, default="BERITA")
    
    penulis = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    published_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "publikasi_informasi"
        ordering = ["-published_at", "-created_at"]

    def save(self, *args, **kwargs):
        # Auto-generate unique slug dari judul jika belum ada
        if not self.slug:
            base_slug = slugify(self.judul)
            unique_slug = base_slug
            counter = 1
            while Publikasi.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.jenis}] {self.judul} ({self.status})"