from django.contrib import admin
from features.profil_wilayah.models import WilayahDusun, WilayahPerangkat, ProfilDesa

@admin.register(WilayahDusun)
class WilayahDusunAdmin(admin.ModelAdmin):
    list_display = ("nama_dusun", "kepala_dusun", "created_at")
    search_fields = ("nama_dusun", "kepala_dusun")

@admin.register(WilayahPerangkat)
class WilayahPerangkatAdmin(admin.ModelAdmin):
    list_display = ("user", "jabatan", "is_published", "created_at")
    list_filter = ("is_published",)
    search_fields = ("user__nama_lengkap", "jabatan")

@admin.register(ProfilDesa)
class ProfilDesaAdmin(admin.ModelAdmin):
    list_display = ("id", "updated_at")
    # Karena Profil Desa konsepnya YAGNI/Singleton (hanya 1 row), 
    # kita tidak perlu filter atau search yang rumit.