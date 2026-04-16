import pytest
from features.pengaduan_warga.domain import (
    STATUS_CLOSED,
    STATUS_IN_PROGRESS,
    STATUS_OPEN,
    STATUS_RESOLVED,
    STATUS_TRIAGED,
    InvalidInputError,
    InvalidStatusTransitionError,
    NoteRequiredError,
    validate_pengaduan_input,
    validate_resolution_note,
    validate_status_transition,
)

class TestDomainPengaduan:
    """Menguji aturan bisnis (Business Rules) dari modul pengaduan."""

    def test_validasi_input_berhasil(self):
        """Test: Input yang memenuhi kriteria harus lolos tanpa error."""
        # Jika tidak raise error, test dianggap passed
        validate_pengaduan_input(
            kategori="Infrastruktur", 
            judul="Jalan berlubang", 
            deskripsi="Ada lubang besar di depan balai desa yang membahayakan."
        )

    def test_validasi_input_judul_terlalu_pendek(self):
        """Test: Judul di bawah 5 karakter harus ditolak."""
        with pytest.raises(InvalidInputError, match="Judul pengaduan terlalu singkat"):
            validate_pengaduan_input("Infrastruktur", "Tes", "Deskripsi yang cukup panjang minimal 10 karakter.")

    def test_transisi_status_valid(self):
        """Test: Transisi dari OPEN ke TRIAGED harus diizinkan."""
        validate_status_transition(STATUS_OPEN, STATUS_TRIAGED)

    def test_transisi_status_invalid(self):
        """Test: Melompat dari OPEN langsung ke RESOLVED tidak diizinkan."""
        with pytest.raises(InvalidStatusTransitionError, match="Tidak dapat mengubah status"):
            validate_status_transition(STATUS_OPEN, STATUS_RESOLVED)

    def test_catatan_wajib_saat_resolved(self):
        """Test: Saat admin merubah status ke RESOLVED, catatan wajib diisi."""
        with pytest.raises(NoteRequiredError, match="Catatan tindak lanjut wajib diisi"):
            validate_resolution_note(STATUS_RESOLVED, notes="")