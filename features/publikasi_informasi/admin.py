# features/publikasi_informasi/admin.py

from django.contrib import admin
from features.publikasi_informasi.models import Publikasi

@admin.register(Publikasi)
class PublikasiAdmin(admin.ModelAdmin):
    list_display = ("judul", "jenis", "status", "published_at")
    list_filter = ("jenis", "status")
    search_fields = ("judul",)
    readonly_fields = ("slug", "created_at", "updated_at")