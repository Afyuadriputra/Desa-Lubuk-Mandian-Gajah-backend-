# features/profil_wilayah/domain.py


class ProfilWilayahError(Exception):
    """Base exception untuk domain profil wilayah."""


class InvalidDataError(ProfilWilayahError):
    """Data input tidak valid."""


def validate_dusun(nama_dusun: str, kepala_dusun: str) -> None:
    nama_dusun = str(nama_dusun or "").strip()
    kepala_dusun = str(kepala_dusun or "").strip()

    if len(nama_dusun) < 3:
        raise InvalidDataError("Nama dusun wajib diisi (minimal 3 karakter).")

    if len(kepala_dusun) < 3:
        raise InvalidDataError("Nama kepala dusun wajib diisi.")


def validate_perangkat(jabatan: str) -> None:
    jabatan = str(jabatan or "").strip()

    if len(jabatan) < 3:
        raise InvalidDataError("Jabatan wajib diisi.")


def validate_profil_desa(visi: str, misi: str, sejarah: str) -> None:
    visi = str(visi or "").strip()
    misi = str(misi or "").strip()
    sejarah = str(sejarah or "").strip()

    if not visi or not misi or not sejarah:
        raise InvalidDataError("Visi, misi, dan sejarah tidak boleh kosong.")