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