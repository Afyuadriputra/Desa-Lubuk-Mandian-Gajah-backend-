# features/pengaduan_warga/domain.py

STATUS_OPEN = "OPEN"
STATUS_TRIAGED = "TRIAGED"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_RESOLVED = "RESOLVED"
STATUS_CLOSED = "CLOSED"

VALID_STATUSES = {
    STATUS_OPEN,
    STATUS_TRIAGED,
    STATUS_IN_PROGRESS,
    STATUS_RESOLVED,
    STATUS_CLOSED,
}

# State Machine Pengaduan
VALID_TRANSITIONS = {
    STATUS_OPEN: {STATUS_TRIAGED, STATUS_CLOSED},  # Bisa langsung ditutup jika spam/invalid
    STATUS_TRIAGED: {STATUS_IN_PROGRESS, STATUS_CLOSED},
    STATUS_IN_PROGRESS: {STATUS_RESOLVED, STATUS_CLOSED},
    STATUS_RESOLVED: {STATUS_CLOSED},
    STATUS_CLOSED: set(),  # Terminal state
}

class PengaduanError(Exception):
    """Base exception untuk domain pengaduan."""

class InvalidStatusTransitionError(PengaduanError):
    """Transisi status tidak diizinkan."""

class NoteRequiredError(PengaduanError):
    """Catatan admin wajib diisi untuk tindakan ini."""

class InvalidInputError(PengaduanError):
    """Input judul, deskripsi, atau kategori tidak valid."""


def validate_pengaduan_input(kategori: str, judul: str, deskripsi: str) -> None:
    if not kategori or not str(kategori).strip():
        raise InvalidInputError("Kategori pengaduan wajib diisi.")
    if not judul or len(str(judul).strip()) < 5:
        raise InvalidInputError("Judul pengaduan terlalu singkat (minimal 5 karakter).")
    if not deskripsi or len(str(deskripsi).strip()) < 10:
        raise InvalidInputError("Deskripsi pengaduan wajib diisi dengan jelas (minimal 10 karakter).")


def validate_status_transition(current_status: str, new_status: str) -> None:
    if new_status not in VALID_STATUSES:
        raise PengaduanError(f"Status '{new_status}' tidak valid.")
    
    allowed_next_statuses = VALID_TRANSITIONS.get(current_status, set())
    if new_status not in allowed_next_statuses:
        raise InvalidStatusTransitionError(
            f"Tidak dapat mengubah status pengaduan dari {current_status} menjadi {new_status}."
        )


def validate_resolution_note(new_status: str, notes: str | None) -> None:
    """Admin wajib memberikan catatan saat status berubah ke RESOLVED atau CLOSED."""
    if new_status in {STATUS_RESOLVED, STATUS_CLOSED}:
        if not notes or not str(notes).strip():
            raise NoteRequiredError(f"Catatan tindak lanjut wajib diisi saat mengubah status menjadi {new_status}.")