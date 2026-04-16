# features/potensi_ekonomi/urls.py

from django.urls import path

from features.potensi_ekonomi.views import (
    buat_unit_usaha_view,
    detail_unit_view,
    katalog_publik_view,
    list_admin_view,
)

urlpatterns = [
    path("ekonomi/katalog/", katalog_publik_view, name="ekonomi-katalog"),
    path("ekonomi/admin/list/", list_admin_view, name="ekonomi-admin-list"),
    path("ekonomi/admin/buat/", buat_unit_usaha_view, name="ekonomi-admin-buat"),
    path("ekonomi/<int:unit_id>/", detail_unit_view, name="ekonomi-detail"),
]