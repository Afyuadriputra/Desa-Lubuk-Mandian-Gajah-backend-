# toolbox/security/upload_validators.py

from pathlib import Path
from django.core.exceptions import ValidationError

DEFAULT_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def get_file_extension(file) -> str:
    return Path(file.name).suffix.lower()


def validate_file_size(file, max_size: int = DEFAULT_MAX_FILE_SIZE) -> None:
    if file.size > max_size:
        raise ValidationError(f"Ukuran file maksimal {max_size // (1024 * 1024)} MB.")


def validate_extension(file, allowed_extensions: set[str]) -> None:
    ext = get_file_extension(file)
    if ext not in allowed_extensions:
        raise ValidationError(
            f"Format file tidak didukung. Format yang diizinkan: {', '.join(sorted(allowed_extensions))}."
        )


def validate_image_upload(file, max_size: int = DEFAULT_MAX_FILE_SIZE) -> None:
    validate_file_size(file, max_size=max_size)
    validate_extension(file, IMAGE_EXTENSIONS)

    content_type = getattr(file, "content_type", "")
    if not content_type.startswith("image/"):
        raise ValidationError("File harus berupa gambar yang valid.")