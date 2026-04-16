# features/pengaduan_warga/urls.py

from django.urls import path

from features.pengaduan_warga.views import (
    buat_pengaduan_view,
    detail_pengaduan_view,
    list_pengaduan_view,
    proses_pengaduan_view,
)

urlpatterns = [
    path("pengaduan/", list_pengaduan_view, name="pengaduan-list"),
    path("pengaduan/buat/", buat_pengaduan_view, name="pengaduan-buat"),
    path("pengaduan/<int:pengaduan_id>/", detail_pengaduan_view, name="pengaduan-detail"),
    path("pengaduan/<int:pengaduan_id>/proses/", proses_pengaduan_view, name="pengaduan-proses"),
]