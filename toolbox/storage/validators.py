# toolbox/storage/validators.py

from pathlib import Path

from django.core.exceptions import ValidationError

MAX_FILENAME_LENGTH = 150


def validate_filename(filename: str) -> None:
    if not filename or not filename.strip():
        raise ValidationError("Nama file tidak boleh kosong.")

    if len(filename) > MAX_FILENAME_LENGTH:
        raise ValidationError(f"Nama file terlalu panjang. Maksimal {MAX_FILENAME_LENGTH} karakter.")


def validate_allowed_extensions(filename: str, allowed_extensions: set[str]) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in allowed_extensions:
        raise ValidationError(
            f"Format file tidak diizinkan. Format yang didukung: {', '.join(sorted(allowed_extensions))}."
        )


def validate_file_size(file, max_size: int) -> None:
    if file.size > max_size:
        raise ValidationError(
            f"Ukuran file melebihi batas maksimum {max_size // (1024 * 1024)} MB."
        )