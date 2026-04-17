# features/profil_wilayah/urls.py

from django.urls import path
from features.profil_wilayah.views import profil_publik_view, tambah_dusun_view, tambah_perangkat_view

urlpatterns = [
    path("profil/publik/", profil_publik_view, name="profil-publik"),
    path("profil/admin/dusun/", tambah_dusun_view, name="admin-dusun-tambah"),
    path("profil/admin/perangkat/", tambah_perangkat_view, name="admin-perangkat-tambah"),
]