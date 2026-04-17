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