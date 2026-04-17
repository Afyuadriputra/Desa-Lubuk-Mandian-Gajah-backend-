# features/publikasi_informasi/urls.py

from django.urls import path
from features.publikasi_informasi.views import (
    list_publikasi_publik_view, 
    detail_publikasi_view, 
    buat_publikasi_admin_view
)

urlpatterns = [
    path("publikasi/", list_publikasi_publik_view, name="publikasi-list-publik"),
    path("publikasi/admin/buat/", buat_publikasi_admin_view, name="publikasi-admin-buat"),
    path("publikasi/<slug:slug>/", detail_publikasi_view, name="publikasi-detail"),
]