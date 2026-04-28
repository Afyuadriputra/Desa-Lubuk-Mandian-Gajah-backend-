# features/layanan_administrasi/domain.py

"""
Layer: Domain

Tanggung jawab:
- Menyimpan aturan bisnis murni.
- Validasi status, keperluan, rejection, dan template surat.
- Tidak import model Django.
- Tidak akses database.
"""


# ============================================================
# Legacy Jenis Surat
# ============================================================
# Catatan:
# - Tetap dipertahankan agar kode lama tidak langsung rusak.
# - Untuk flow baru, jenis surat idealnya berasal dari TemplateSurat.
# ============================================================

JENIS_SKU = "SKU"
JENIS_SKTM = "SKTM"
JENIS_DOMISILI = "DOMISILI"

VALID_JENIS_SURAT = {JENIS_SKU, JENIS_SKTM, JENIS_DOMISILI}


# ============================================================
# Status Surat
# ============================================================

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


# ============================================================
# State Machine
# ============================================================
# Aturan:
# - PENDING    -> VERIFIED / REJECTED
# - VERIFIED   -> PROCESSED / REJECTED
# - PROCESSED  -> DONE / REJECTED
# - DONE       -> terminal
# - REJECTED   -> terminal
# ============================================================

VALID_TRANSITIONS = {
    STATUS_PENDING: {STATUS_VERIFIED, STATUS_REJECTED},
    STATUS_VERIFIED: {STATUS_PROCESSED, STATUS_REJECTED},
    STATUS_PROCESSED: {STATUS_DONE, STATUS_REJECTED},
    STATUS_DONE: set(),
    STATUS_REJECTED: set(),
}


# ============================================================
# Template Surat Rules
# ============================================================

TEMPLATE_DOCX_EXTENSION = ".docx"

SUPPORTED_TEMPLATE_PLACEHOLDERS = {
    "{{ nomor_surat }}",
    "{{ tanggal_cetak }}",
    "{{ nama_kepala_desa }}",
    "{{ surat.jenis_surat }}",
    "{{ surat.keperluan }}",
    "{{ surat.status }}",
    "{{ surat.created_at }}",
    "{{ pemohon.nama_lengkap }}",
    "{{ pemohon.nik }}",
    "{{ pemohon.nomor_hp }}",
    "{{ pemohon.email }}",
}


# ============================================================
# Domain Exceptions
# ============================================================

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


class InvalidTemplateSuratError(LayananSuratError):
    """Template surat tidak valid."""


class InvalidTemplateFileError(LayananSuratError):
    """File template surat tidak valid."""


# ============================================================
# Small Helpers
# ============================================================

def normalize_template_code(kode: str) -> str:
    """
    Menormalkan kode template agar konsisten.

    Contoh:
    - " sku " -> "SKU"
    - "surat-domisili" -> "SURAT-DOMISILI"
    """
    return str(kode or "").strip().upper()


# ============================================================
# Validasi Surat
# ============================================================

def validate_jenis_surat(jenis: str) -> None:
    """
    Validasi legacy jenis_surat.

    Catatan:
    - Masih dipakai untuk kompatibilitas kode lama.
    - Untuk flow baru, validasi utama sebaiknya melalui TemplateSurat aktif.
    """
    if jenis not in VALID_JENIS_SURAT:
        raise InvalidJenisSuratError(f"Jenis surat '{jenis}' tidak valid.")


def validate_keperluan(keperluan: str | None) -> None:
    if not keperluan or not str(keperluan).strip():
        raise InvalidKeperluanError("Keperluan pengajuan surat wajib diisi.")

    if len(str(keperluan).strip()) < 10:
        raise InvalidKeperluanError("Deskripsi keperluan terlalu singkat, minimal 10 karakter.")


def validate_status_transition(current_status: str, new_status: str) -> None:
    if new_status not in VALID_STATUSES:
        raise LayananSuratError(f"Status '{new_status}' tidak dikenali.")

    allowed_next_statuses = VALID_TRANSITIONS.get(current_status, set())
    if new_status not in allowed_next_statuses:
        raise InvalidStatusTransitionError(
            f"Tidak dapat mengubah status dari {current_status} menjadi {new_status}."
        )


def validate_rejection(status: str, rejection_reason: str | None) -> None:
    if status != STATUS_REJECTED:
        return

    if not rejection_reason or not str(rejection_reason).strip():
        raise RejectionReasonRequiredError("Alasan penolakan wajib diisi.")


# ============================================================
# Validasi Template Surat
# ============================================================

def validate_template_code(kode: str | None) -> None:
    if not kode or not str(kode).strip():
        raise InvalidTemplateSuratError("Kode template surat wajib diisi.")

    normalized_kode = normalize_template_code(kode)

    if len(normalized_kode) < 2:
        raise InvalidTemplateSuratError("Kode template surat terlalu pendek.")

    if len(normalized_kode) > 50:
        raise InvalidTemplateSuratError("Kode template surat maksimal 50 karakter.")


def validate_template_name(nama: str | None) -> None:
    if not nama or not str(nama).strip():
        raise InvalidTemplateSuratError("Nama template surat wajib diisi.")

    if len(str(nama).strip()) < 3:
        raise InvalidTemplateSuratError("Nama template surat terlalu pendek.")


def validate_template_file(filename: str | None) -> None:
    if not filename or not str(filename).strip():
        raise InvalidTemplateFileError("File template surat wajib diunggah.")

    if not str(filename).lower().endswith(TEMPLATE_DOCX_EXTENSION):
        raise InvalidTemplateFileError("File template surat harus berformat .docx.")


def validate_template_is_active(template) -> None:
    """
    Validasi template aktif.

    Parameter sengaja generic agar domain.py tidak bergantung ke model Django.
    """
    if not template:
        raise InvalidTemplateSuratError("Template surat tidak ditemukan.")

    if not getattr(template, "is_active", False):
        raise InvalidTemplateSuratError("Template surat tidak aktif.")