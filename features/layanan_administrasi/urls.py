# features/layanan_administrasi/urls.py

from django.urls import path

from features.layanan_administrasi.views import (
    ajukan_surat_view,
    detail_surat_view,
    list_surat_view,
    proses_surat_view,
)

urlpatterns = [
    path("surat/", list_surat_view, name="surat-list"),
    path("surat/ajukan/", ajukan_surat_view, name="surat-ajukan"),
    path("surat/<uuid:surat_id>/", detail_surat_view, name="surat-detail"),
    path("surat/<uuid:surat_id>/proses/", proses_surat_view, name="surat-proses"),
]