# LLM Context: Tests untuk fitur `publikasi_informasi`

Dokumen ini berisi kumpulan kode dari direktori `publikasi_informasi/tests` untuk keperluan konteks LLM.

---
## File: `publikasi_informasi/tests/test_api.py`

```python
# features/publikasi_informasi/tests/test_api.py
import pytest
import json
from features.publikasi_informasi.models import Publikasi

@pytest.mark.django_db
class TestPublikasiAPI:

    def test_buat_publikasi_otomatis_slug_dan_sanitasi(self, client, admin_user):
        client.force_login(admin_user)
        payload = {
            "judul": "Pengumuman Desa",
            "konten_html": "<h1>Info</h1><script>alert(1)</script>",
            "jenis": "PENGUMUMAN",
            "status": "DRAFT"
        }
        response = client.post("/api/v1/publikasi/admin/buat", data=json.dumps(payload), content_type="application/json")
        
        assert response.status_code == 201
        data = response.json()
        assert "pengumuman-desa" in data["slug"]
        assert "<script>" not in data["konten_html"]

    def test_publikasi_list_tidak_mengirim_html_panjang(self, client):
        Publikasi.objects.create(judul="Berita 1", slug="berita-1", konten_html="<p>Isi panjang</p>", status="PUBLISHED")
        response = client.get("/api/v1/publikasi/publik")
        
        assert response.status_code == 200
        data = response.json()
        assert "konten_html" not in data[0]
```

---
## File: `publikasi_informasi/tests/test_domain.py`

```python
import pytest
from features.publikasi_informasi.domain import (
    JENIS_BERITA,
    JENIS_PENGUMUMAN,
    STATUS_DRAFT,
    STATUS_PUBLISHED,
    PublikasiError,
    validate_publikasi_input,
)

class TestDomainPublikasi:
    def test_validasi_input_sukses_jika_data_sesuai(self):
        # YAGNI: Tes berhasil jika tidak ada exception yang terlempar
        validate_publikasi_input(
            judul="Rapat Desa 2026",
            konten_html="<p>Ini adalah konten yang cukup panjang.</p>",
            jenis=JENIS_BERITA,
            status=STATUS_PUBLISHED
        )

    def test_validasi_gagal_jika_judul_terlalu_pendek(self):
        with pytest.raises(PublikasiError, match="Judul terlalu pendek"):
            validate_publikasi_input("Tes", "<p>Konten panjang...</p>", JENIS_BERITA, STATUS_DRAFT)

    def test_validasi_gagal_jika_konten_terlalu_pendek(self):
        # "<p>A</p>" panjangnya 8 karakter (kurang dari 10) sehingga akan memicu error
        with pytest.raises(PublikasiError, match="Konten tidak boleh kosong"):
            validate_publikasi_input("Judul Valid", "<p>A</p>", JENIS_PENGUMUMAN, STATUS_DRAFT)

    def test_validasi_gagal_jika_jenis_tidak_dikenali(self):
        with pytest.raises(PublikasiError, match="tidak dikenali"):
            validate_publikasi_input("Judul Valid", "<p>Konten panjang...</p>", "JENIS_ANEH", STATUS_DRAFT)

    def test_validasi_gagal_jika_status_tidak_dikenali(self):
        with pytest.raises(PublikasiError, match="tidak valid"):
            validate_publikasi_input("Judul Valid", "<p>Konten panjang...</p>", JENIS_BERITA, "STATUS_ANEH")
```

---
## File: `publikasi_informasi/tests/test_repositories.py`

```python
import pytest
from features.publikasi_informasi.models import Publikasi
from features.publikasi_informasi.repositories import PublikasiRepository
from features.publikasi_informasi.domain import STATUS_PUBLISHED, STATUS_DRAFT, JENIS_BERITA, JENIS_PENGUMUMAN

pytestmark = pytest.mark.django_db

class TestPublikasiRepositoryDanModel:
    def test_model_auto_generate_slug_yang_unik(self):
        """Membuktikan model menambahkan angka (-1, -2) jika judul sama."""
        repo = PublikasiRepository()
        
        # Buat publikasi pertama
        pub1 = repo.create({"judul": "Berita Desa", "konten_html": "Tes 123", "status": STATUS_DRAFT})
        assert pub1.slug == "berita-desa"
        
        # Buat publikasi kedua dengan judul yang sama persis
        pub2 = repo.create({"judul": "Berita Desa", "konten_html": "Tes 123", "status": STATUS_DRAFT})
        assert pub2.slug == "berita-desa-1"
        
        # Buat publikasi ketiga
        pub3 = repo.create({"judul": "Berita Desa", "konten_html": "Tes 123", "status": STATUS_DRAFT})
        assert pub3.slug == "berita-desa-2"

    def test_repo_list_published_bisa_filter_berdasarkan_jenis(self):
        repo = PublikasiRepository()
        repo.create({"judul": "Berita 1", "konten_html": "A", "status": STATUS_PUBLISHED, "jenis": JENIS_BERITA})
        repo.create({"judul": "Pengumuman 1", "konten_html": "B", "status": STATUS_PUBLISHED, "jenis": JENIS_PENGUMUMAN})
        repo.create({"judul": "Berita Draft", "konten_html": "C", "status": STATUS_DRAFT, "jenis": JENIS_BERITA})

        hasil_semua_published = repo.list_published()
        assert hasil_semua_published.count() == 2

        hasil_berita_saja = repo.list_published(jenis=JENIS_BERITA)
        assert hasil_berita_saja.count() == 1
        assert hasil_berita_saja.first().judul == "Berita 1"
```

---
## File: `publikasi_informasi/tests/test_services.py`

```python
import pytest
from pytest_mock import mocker
from features.publikasi_informasi.domain import STATUS_DRAFT, STATUS_PUBLISHED, JENIS_BERITA
from features.publikasi_informasi.services import PublikasiService, PublikasiAccessError, PublikasiError

class TestPublikasiService:
    @pytest.fixture
    def mock_repo(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def service(self, mock_repo):
        # Dependency Inversion: Inject mock ke dalam service
        return PublikasiService(repo=mock_repo)

    @pytest.fixture
    def mock_admin(self, mocker):
        return mocker.Mock(id=1)

    def test_buat_publikasi_ditolak_jika_tanpa_akses(self, service, mock_admin, mocker):
        mocker.patch("features.publikasi_informasi.services.can_create_or_edit_publikasi", return_value=False)
        
        with pytest.raises(PublikasiAccessError, match="tidak memiliki izin"):
            service.buat_publikasi(mock_admin, "Judul Valid", "<p>Konten panjang</p>", JENIS_BERITA, STATUS_DRAFT)

    # PERBAIKAN: Tambahkan 'mocker' di dalam kurung parameter di bawah ini
    def test_get_detail_publik_menolak_data_draft(self, service, mock_repo, mocker):
        # Setup mock agar repo mengembalikan data bersatus DRAFT
        mock_publikasi = mocker.Mock(status=STATUS_DRAFT)
        mock_repo.get_by_slug.return_value = mock_publikasi
        
        with pytest.raises(PublikasiError, match="belum dipublikasikan"):
            service.get_detail_publik("slug-rahasia")
```

---
## File: `publikasi_informasi/tests/__init__.py`

```python

```

