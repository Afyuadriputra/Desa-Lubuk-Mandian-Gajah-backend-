# features/profil_wilayah/domain.py

class ProfilWilayahError(Exception):
    """Base exception untuk domain profil wilayah."""

class InvalidDataError(ProfilWilayahError):
    """Data input tidak valid."""

def validate_dusun(nama_dusun: str, kepala_dusun: str) -> None:
    if not nama_dusun or len(str(nama_dusun).strip()) < 3:
        raise InvalidDataError("Nama dusun wajib diisi (minimal 3 karakter).")
    if not kepala_dusun or len(str(kepala_dusun).strip()) < 3:
        raise InvalidDataError("Nama kepala dusun wajib diisi.")

def validate_perangkat(jabatan: str) -> None:
    if not jabatan or len(str(jabatan).strip()) < 3:
        raise InvalidDataError("Jabatan wajib diisi.")

def validate_profil_desa(visi: str, misi: str, sejarah: str) -> None:
    if not visi or not misi or not sejarah:
        raise InvalidDataError("Visi, misi, dan sejarah tidak boleh kosong.")