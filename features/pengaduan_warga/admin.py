from django.contrib import admin
from features.pengaduan_warga.models import LayananPengaduan, LayananPengaduanHistory

# Inline agar histori status bisa dilihat langsung di halaman detail pengaduan
class LayananPengaduanHistoryInline(admin.TabularInline):
    model = LayananPengaduanHistory
    extra = 0
    # Dibuat readonly agar admin tidak memanipulasi log audit
    readonly_fields = ("status_from", "status_to", "changed_by", "notes", "created_at")
    can_delete = False

@admin.register(LayananPengaduan)
class LayananPengaduanAdmin(admin.ModelAdmin):
    list_display = ("id", "pelapor", "kategori", "judul", "status", "created_at")
    list_filter = ("status", "kategori")
    search_fields = ("pelapor__nama_lengkap", "judul", "pelapor__nik")
    inlines = [LayananPengaduanHistoryInline]
    readonly_fields = ("created_at", "updated_at")

# Mendaftarkan histori secara terpisah jika admin ingin melihat semua log
@admin.register(LayananPengaduanHistory)
class LayananPengaduanHistoryAdmin(admin.ModelAdmin):
    list_display = ("pengaduan", "status_from", "status_to", "changed_by", "created_at")
    list_filter = ("status_to",)
    search_fields = ("pengaduan__judul", "notes")
    # Mengunci semua field agar murni sebagai log baca-saja
    readonly_fields = ("pengaduan", "status_from", "status_to", "changed_by", "notes", "created_at")