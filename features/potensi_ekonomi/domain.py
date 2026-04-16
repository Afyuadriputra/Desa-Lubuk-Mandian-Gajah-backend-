# features/potensi_ekonomi/domain.py

KATEGORI_KOPERASI = "KOPERASI"
KATEGORI_WISATA = "WISATA"
KATEGORI_JASA = "JASA"

VALID_KATEGORI = {
    KATEGORI_KOPERASI,
    KATEGORI_WISATA,
    KATEGORI_JASA,
}

class PotensiEkonomiError(Exception):
    """Base exception untuk domain potensi ekonomi."""

class InvalidKategoriError(PotensiEkonomiError):
    """Kategori unit usaha tidak valid."""

class InvalidInputError(PotensiEkonomiError):
    """Input deskripsi atau kontak tidak valid."""

def validate_kategori(kategori: str) -> None:
    if kategori not in VALID_KATEGORI:
        raise InvalidKategoriError(f"Kategori '{kategori}' tidak valid.")

def validate_input_usaha(nama_usaha: str, kontak_wa: str) -> None:
    if not nama_usaha or len(str(nama_usaha).strip()) < 3:
        raise InvalidInputError("Nama usaha wajib diisi (minimal 3 karakter).")
    
    if kontak_wa:
        cleaned_wa = str(kontak_wa).replace("+", "").replace("-", "").strip()
        if not cleaned_wa.isdigit():
            raise InvalidInputError("Kontak WA hanya boleh berisi angka (dan tanda +).")