from django.contrib import admin
from features.potensi_ekonomi.models import BumdesUnitUsaha

@admin.register(BumdesUnitUsaha)
class BumdesUnitUsahaAdmin(admin.ModelAdmin):
    list_display = ("nama_usaha", "kategori", "is_published", "harga_tiket", "created_at")
    list_filter = ("kategori", "is_published")
    search_fields = ("nama_usaha",)