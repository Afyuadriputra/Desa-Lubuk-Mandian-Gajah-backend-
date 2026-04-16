# features/layanan_administrasi/admin.py

from django.contrib import admin
from features.layanan_administrasi.models import LayananSurat, LayananSuratStatusHistory

class LayananSuratStatusHistoryInline(admin.TabularInline):
    model = LayananSuratStatusHistory
    extra = 0
    readonly_fields = ("status_from", "status_to", "changed_by", "notes", "created_at")

@admin.register(LayananSurat)
class LayananSuratAdmin(admin.ModelAdmin):
    list_display = ("id", "pemohon", "jenis_surat", "status", "created_at")
    list_filter = ("status", "jenis_surat")
    search_fields = ("pemohon__nama_lengkap", "pemohon__nik", "nomor_surat")
    inlines = [LayananSuratStatusHistoryInline]
    readonly_fields = ("id", "created_at", "updated_at")