# core_django/urls.py

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("features.auth_warga.urls")),
    path("api/layanan-administrasi/", include("features.layanan_administrasi.urls")),
    path("api/pengaduan/", include("features.pengaduan_warga.urls")),
    path("api/potensi-ekonomi/", include("features.potensi_ekonomi.urls")),
    path("api/profil-wilayah/", include("features.profil_wilayah.urls")),
    path("api/publikasi/", include("features.publikasi_informasi.urls")),
]