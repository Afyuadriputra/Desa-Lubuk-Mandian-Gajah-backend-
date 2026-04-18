import pytest
from django.urls import reverse
from features.potensi_ekonomi.models import BumdesUnitUsaha

@pytest.mark.django_db
class TestPotensiEkonomiAPI:
    
    def test_warga_bisa_lihat_katalog_publik(self, client, warga_user):
        """Memastikan endpoint katalog publik bisa diakses warga dan isinya tersanitasi."""
        client.force_login(warga_user)
        
        # Setup data awal
        BumdesUnitUsaha.objects.create(
            nama_usaha="Kolam Renang",
            kategori="WISATA",
            deskripsi="Kolam jernih",
            is_published=True
        )

        # Asumsikan endpoint di-mount di /api/v1/potensi-ekonomi/katalog
        response = client.get("/api/v1/potensi-ekonomi/katalog")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["nama_usaha"] == "Kolam Renang"
        # YAGNI check: Pastikan 'is_published' tidak bocor ke publik
        assert "is_published" not in data[0]

    def test_buat_unit_usaha_dengan_xss_otomatis_bersih(self, client, admin_user):
        """Memastikan Pydantic SafeHTMLString membersihkan script berbahaya."""
        client.force_login(admin_user)
        
        payload = {
            "nama_usaha": "Toko BUMDes",
            "kategori": "KOPERASI",
            # Mengandung XSS jahat
            "deskripsi": "<p>Toko murah</p><script>alert('hack')</script>",
            "is_published": "true"
        }

        response = client.post("/api/v1/potensi-ekonomi/admin/buat", data=payload)
        
        assert response.status_code == 201
        
        # Cek ke database apakah tersanitasi
        unit = BumdesUnitUsaha.objects.get(nama_usaha="Toko BUMDes")
        assert "<script>" not in unit.deskripsi
        assert "<p>Toko murah</p>" in unit.deskripsi  # Tag aman dipertahankan

    def test_warga_ditolak_saat_buat_unit(self, client, warga_user):
        """Validasi class AuthAdminOnly bekerja di level Ninja."""
        client.force_login(warga_user)
        
        payload = {"nama_usaha": "Illegal", "kategori": "JASA", "deskripsi": "Test"}
        response = client.post("/api/v1/potensi-ekonomi/admin/buat", data=payload)
        
        # 403 Forbidden karena middleware AuthAdminOnly menolak akses
        assert response.status_code == 403