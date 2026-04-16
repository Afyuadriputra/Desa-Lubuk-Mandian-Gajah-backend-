# features/layanan_administrasi/domain.py

JENIS_SKU = "SKU"
JENIS_SKTM = "SKTM"
JENIS_DOMISILI = "DOMISILI"

VALID_JENIS_SURAT = {JENIS_SKU, JENIS_SKTM, JENIS_DOMISILI}

STATUS_PENDING = "PENDING"
STATUS_VERIFIED = "VERIFIED"
STATUS_PROCESSED = "PROCESSED"
STATUS_DONE = "DONE"
STATUS_REJECTED = "REJECTED"

VALID_STATUSES = {
    STATUS_PENDING,
    STATUS_VERIFIED,
    STATUS_PROCESSED,
    STATUS_DONE,
    STATUS_REJECTED,
}

# State Machine: Menentukan status apa saja yang valid untuk dituju dari status saat ini
VALID_TRANSITIONS = {
    STATUS_PENDING: {STATUS_VERIFIED, STATUS_REJECTED},
    STATUS_VERIFIED: {STATUS_PROCESSED, STATUS_REJECTED},
    STATUS_PROCESSED: {STATUS_DONE, STATUS_REJECTED},
    STATUS_DONE: set(),      # Terminal state
    STATUS_REJECTED: set(),  # Terminal state
}


class LayananSuratError(Exception):
    """Base exception untuk domain layanan surat."""


class InvalidJenisSuratError(LayananSuratError):
    """Jenis surat tidak valid."""


class InvalidStatusTransitionError(LayananSuratError):
    """Transisi status tidak diizinkan."""


class InvalidKeperluanError(LayananSuratError):
    """Keperluan surat tidak valid atau kosong."""


class RejectionReasonRequiredError(LayananSuratError):
    """Alasan penolakan wajib diisi jika status REJECTED."""


def validate_jenis_surat(jenis: str) -> None:
    if jenis not in VALID_JENIS_SURAT:
        raise InvalidJenisSuratError(f"Jenis surat '{jenis}' tidak valid.")


def validate_keperluan(keperluan: str | None) -> None:
    if not keperluan or not str(keperluan).strip():
        raise InvalidKeperluanError("Keperluan pengajuan surat wajib diisi.")
    if len(str(keperluan)) < 10:
        raise InvalidKeperluanError("Deskripsi keperluan terlalu singkat (minimal 10 karakter).")


def validate_status_transition(current_status: str, new_status: str) -> None:
    if new_status not in VALID_STATUSES:
        raise LayananSuratError(f"Status '{new_status}' tidak dikenali.")
    
    allowed_next_statuses = VALID_TRANSITIONS.get(current_status, set())
    if new_status not in allowed_next_statuses:
        raise InvalidStatusTransitionError(
            f"Tidak dapat mengubah status dari {current_status} menjadi {new_status}."
        )


def validate_rejection(status: str, rejection_reason: str | None) -> None:
    if status == STATUS_REJECTED:
        if not rejection_reason or not str(rejection_reason).strip():
            raise RejectionReasonRequiredError("Alasan penolakan wajib diisi.")