# core_django/urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .api_v1 import api  # Import dari file pengumpul API v1

urlpatterns = [
    path("admin/", admin.site.urls),

    # Semua routing fitur otomatis di-handle oleh Django Ninja
    path("api/v1/", include(api.urls[0])),
]

# Development only: agar file upload di MEDIA_ROOT bisa diakses lewat /media/
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)