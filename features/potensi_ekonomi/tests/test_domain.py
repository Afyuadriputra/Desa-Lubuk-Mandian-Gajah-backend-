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