# LLM Context: Tests untuk fitur `potensi_ekonomi`

Dokumen ini berisi kumpulan kode dari direktori `potensi_ekonomi/tests` untuk keperluan konteks LLM.

---
## File: `potensi_ekonomi/tests/test_api.py`

```python
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
```

---
## File: `potensi_ekonomi/tests/test_domain.py`

```python
import pytest
from features.potensi_ekonomi.domain import (
    KATEGORI_JASA,
    KATEGORI_KOPERASI,
    KATEGORI_WISATA,
    InvalidInputError,
    InvalidKategoriError,
    validate_input_usaha,
    validate_kategori,
)

class TestDomainPotensiEkonomi:
    def test_validasi_kategori_berhasil(self):
        validate_kategori(KATEGORI_WISATA)
        validate_kategori(KATEGORI_KOPERASI)
        validate_kategori(KATEGORI_JASA)

    def test_validasi_kategori_gagal_jika_tidak_dikenal(self):
        with pytest.raises(InvalidKategoriError, match="tidak valid"):
            validate_kategori("ILEGAL_KATEGORI")

    def test_validasi_input_usaha_berhasil(self):
        # Harus lolos tanpa error
        validate_input_usaha(nama_usaha="Taman Wisata", kontak_wa="+628123456789")
        validate_input_usaha(nama_usaha="Kop", kontak_wa="") # Minimal 3 huruf, WA opsional

    def test_validasi_nama_usaha_terlalu_pendek(self):
        # Ubah "Minimal" menjadi "minimal" agar match dengan pesan error aslinya
        with pytest.raises(InvalidInputError, match="minimal 3 karakter"):
            validate_input_usaha(nama_usaha="Ab", kontak_wa="")

    def test_validasi_kontak_wa_mengandung_huruf(self):
        with pytest.raises(InvalidInputError, match="hanya boleh berisi angka"):
            validate_input_usaha(nama_usaha="BUMDes Jaya", kontak_wa="08123abcd")
```

---
## File: `potensi_ekonomi/tests/test_repositories.py`

```python
import pytest
from features.potensi_ekonomi.models import BumdesUnitUsaha
from features.potensi_ekonomi.repositories import UnitUsahaRepository

pytestmark = pytest.mark.django_db

class TestUnitUsahaRepository:
    def test_list_published_hanya_mengembalikan_yang_aktif(self):
        repo = UnitUsahaRepository()
        
        # Buat 1 Draft, 1 Published
        repo.create_unit({
            "nama_usaha": "Koperasi Draft", 
            "kategori": "KOPERASI", 
            "deskripsi": "Tes", 
            "is_published": False
        })
        repo.create_unit({
            "nama_usaha": "Wisata Aktif", 
            "kategori": "WISATA", 
            "deskripsi": "Tes", 
            "is_published": True
        })

        hasil_published = repo.list_published()
        hasil_semua = repo.list_all()

        assert hasil_semua.count() == 2
        assert hasil_published.count() == 1
        assert hasil_published.first().nama_usaha == "Wisata Aktif"

    def test_update_dan_delete_unit_bekerja_dengan_baik(self):
        repo = UnitUsahaRepository()
        unit = repo.create_unit({"nama_usaha": "Lama", "kategori": "JASA", "deskripsi": ""})
        
        # Test Update
        unit_updated = repo.update_unit(unit, {"nama_usaha": "Baru", "is_published": True})
        assert unit_updated.nama_usaha == "Baru"
        assert unit_updated.is_published is True

        # Test Delete
        repo.delete_unit(unit_updated)
        assert repo.list_all().count() == 0
```

---
## File: `potensi_ekonomi/tests/test_services.py`

```python
import pytest
from django.core.exceptions import ValidationError
from features.potensi_ekonomi.domain import KATEGORI_WISATA
from features.potensi_ekonomi.models import BumdesUnitUsaha
from features.potensi_ekonomi.services import (
    FileUploadError,
    PermissionDeniedError,
    PotensiEkonomiService,
    UnitUsahaNotFoundError,
)

class TestPotensiEkonomiService:
    @pytest.fixture
    def mock_repo(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def service(self, mock_repo):
        return PotensiEkonomiService(repository=mock_repo)

    @pytest.fixture
    def mock_admin(self, mocker):
        user = mocker.Mock()
        user.id = 1
        user.role = "ADMIN" # Asumsi role admin bisa manage
        user.is_authenticated = True
        user.is_active = True
        return user

    @pytest.fixture
    def mock_warga(self, mocker):
        user = mocker.Mock()
        user.id = 2
        user.role = "WARGA"
        user.is_authenticated = True
        user.is_active = True
        return user

    def test_warga_tidak_bisa_buat_unit_usaha(self, service, mock_warga):
        with pytest.raises(PermissionDeniedError, match="Anda tidak memiliki izin"):
            service.buat_unit_usaha(mock_warga, {"nama_usaha": "Taman", "kategori": KATEGORI_WISATA})

    def test_warga_tidak_bisa_lihat_detail_draft(self, service, mock_warga, mock_repo, mocker):
        """Test: Mencegah Warga melihat Unit Usaha yang is_published=False."""
        mocker.patch("features.potensi_ekonomi.permissions.can_manage_data_bumdes", return_value=False)
        mocker.patch("features.potensi_ekonomi.permissions.can_view_katalog_publik", return_value=True)
        
        mock_draft = mocker.Mock(is_published=False)
        mock_repo.get_by_id.return_value = mock_draft

        with pytest.raises(PermissionDeniedError, match="belum tersedia untuk publik"):
            service.get_detail_unit(mock_warga, unit_id=99)
```

---
## File: `potensi_ekonomi/tests/__init__.py`

```python

```

