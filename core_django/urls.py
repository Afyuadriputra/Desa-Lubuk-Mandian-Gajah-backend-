# core_django/urls.py

from django.contrib import admin
from django.urls import path
from .api_v1 import api  # Import dari file pengumpul yang kita buat di Langkah 2

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # HANYA INI SAJA! Semua routing fitur otomatis di-handle oleh Ninja
    path("api/v1/", api.urls), 
]