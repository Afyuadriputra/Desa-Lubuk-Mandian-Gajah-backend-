# features/layanan_administrasi/admin.py

"""
Layer: Admin

Tanggung jawab:
- Konfigurasi tampilan Django Admin.
- Tidak berisi business logic.
"""

from django.contrib import admin

from features.layanan_administrasi.models import (
    LayananSurat,
    LayananSuratStatusHistory,
    TemplateSurat,
)


# ============================================================
# Template Surat Admin
# ============================================================

@admin.register(TemplateSurat)
class TemplateSuratAdmin(admin.ModelAdmin):
    list_display = ("kode", "nama", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("kode", "nama", "deskripsi")
    readonly_fields = ("created_at", "updated_at")


# ============================================================
# Layanan Surat Admin
# ============================================================

class LayananSuratStatusHistoryInline(admin.TabularInline):
    model = LayananSuratStatusHistory
    extra = 0
    readonly_fields = ("status_from", "status_to", "changed_by", "notes", "created_at")
    can_delete = False


@admin.register(LayananSurat)
class LayananSuratAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "pemohon",
        "jenis_surat",
        "template",
        "status",
        "created_at",
    )
    list_filter = ("status", "jenis_surat", "template")
    search_fields = (
        "pemohon__nama_lengkap",
        "pemohon__nik",
        "nomor_surat",
        "template__kode",
        "template__nama",
    )
    readonly_fields = (
        "id",
        "pdf_file",
        "docx_file",
        "created_at",
        "updated_at",
    )
    inlines = [LayananSuratStatusHistoryInline]


# ============================================================
# Histori Status Admin
# ============================================================

@admin.register(LayananSuratStatusHistory)
class LayananSuratStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("surat", "status_from", "status_to", "changed_by", "created_at")
    list_filter = ("status_to",)
    search_fields = ("surat__nomor_surat", "notes")
    readonly_fields = (
        "surat",
        "status_from",
        "status_to",
        "changed_by",
        "notes",
        "created_at",
    )