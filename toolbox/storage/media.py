# toolbox/storage/media.py

from pathlib import Path
from uuid import uuid4

from django.utils.text import slugify


def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def get_file_stem(filename: str) -> str:
    return Path(filename).stem


def make_safe_filename(filename: str, prefix: str | None = None) -> str:
    ext = get_file_extension(filename)
    stem = slugify(get_file_stem(filename)) or "file"
    unique_id = uuid4().hex[:12]

    if prefix:
        safe_prefix = slugify(prefix)
        return f"{safe_prefix}-{stem}-{unique_id}{ext}"

    return f"{stem}-{unique_id}{ext}"