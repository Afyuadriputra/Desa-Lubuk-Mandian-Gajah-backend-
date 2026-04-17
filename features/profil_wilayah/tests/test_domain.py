import pytest
from features.profil_wilayah.domain import (
    InvalidDataError,
    validate_dusun,
    validate_perangkat,
    validate_profil_desa,
)

class TestDomainProfilWilayah:
    # --- Validasi Dusun ---
    def test_validasi_dusun_harus_sukses_jika_data_valid(self):
        validate_dusun(nama_dusun="Mawar", kepala_dusun="Pak Budi")  # Tidak boleh error

    def test_validasi_dusun_harus_gagal_jika_nama_terlalu_pendek(self):
        with pytest.raises(InvalidDataError, match="minimal 3 karakter"):
            validate_dusun(nama_dusun="AB", kepala_dusun="Pak Budi")

    def test_validasi_dusun_harus_gagal_jika_kepala_dusun_kosong(self):
        with pytest.raises(InvalidDataError, match="kepala dusun wajib diisi"):
            validate_dusun(nama_dusun="Melati", kepala_dusun="   ")

    # --- Validasi Perangkat ---
    def test_validasi_perangkat_harus_sukses_jika_jabatan_valid(self):
        validate_perangkat(jabatan="Sekretaris Desa")

    def test_validasi_perangkat_harus_gagal_jika_jabatan_kosong(self):
        with pytest.raises(InvalidDataError, match="Jabatan wajib diisi"):
            validate_perangkat(jabatan="")

    # --- Validasi Profil Desa ---
    def test_validasi_profil_desa_harus_sukses_jika_lengkap(self):
        validate_profil_desa(visi="Maju", misi="Bersama", sejarah="Tahun 1990")

    def test_validasi_profil_desa_harus_gagal_jika_ada_yang_kosong(self):
        with pytest.raises(InvalidDataError, match="tidak boleh kosong"):
            validate_profil_desa(visi="Maju", misi="", sejarah="Tahun 1990")