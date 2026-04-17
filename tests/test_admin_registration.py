# tests/test_admin_registration.py

import pytest
from django.apps import apps
from django.contrib import admin

@pytest.mark.django_db
def test_semua_model_features_terdaftar_di_admin():
    """
    Memastikan seluruh model database yang ada di dalam folder 'features'
    sudah didaftarkan ke halaman Admin Django.
    """
    model_belum_terdaftar = []

    # Ambil semua aplikasi yang ter-install
    for app_config in apps.get_app_configs():
        # Batasi hanya pada aplikasi buatan kita di folder 'features'
        if app_config.name.startswith('features.'):
            # Ambil semua model di dalam aplikasi tersebut
            for model in app_config.get_models():
                # Cek apakah model sudah diregister ke admin site
                if not admin.site.is_registered(model):
                    model_belum_terdaftar.append(f"{model.__name__} (dari {app_config.name})")

    # Test akan GAGAL jika list model_belum_terdaftar tidak kosong
    pesan_error = "❌ Ada model yang lupa didaftarkan ke admin.py:\n" + "\n".join(model_belum_terdaftar)
    assert len(model_belum_terdaftar) == 0, pesan_error