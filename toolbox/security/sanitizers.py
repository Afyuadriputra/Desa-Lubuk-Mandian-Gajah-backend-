# toolbox/security/sanitizers.py

import bleach
from typing import Annotated
from pydantic import BeforeValidator

ALLOWED_TAGS = [
    "p", "br", "strong", "em", "u", "b", "i", 
    "ul", "ol", "li",
    "blockquote",
    "h1", "h2", "h3", "h4",
    "a",
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "target", "rel"],
}

ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def sanitize_html(value: str | None) -> str:
    if not value:
        return ""
    return bleach.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )


def sanitize_plain_text(value: str | None) -> str:
    if not value:
        return ""
    return bleach.clean(value, tags=[], attributes={}, strip=True).strip()


def sanitize_rich_text_content(value: str | None) -> str:
    return sanitize_html(value)


# =====================================================================
# PYDANTIC INTEGRATION UNTUK DJANGO NINJA (API LAYER)
# =====================================================================

def _pydantic_html_validator(value: str | None) -> str | None:
    """Validator internal untuk membersihkan input HTML pada Pydantic Schema."""
    if not isinstance(value, str):
        return value
    return sanitize_rich_text_content(value)


def _pydantic_plain_text_validator(value: str | None) -> str | None:
    """Validator internal untuk membersihkan input teks biasa pada Pydantic Schema."""
    if not isinstance(value, str):
        return value
    return sanitize_plain_text(value)


# Custom Types yang siap di-import dan digunakan langsung di schemas.py
# Pydantic akan secara otomatis menjalankan fungsi sanitasi sebelum data masuk ke service layer.

SafeHTMLString = Annotated[str, BeforeValidator(_pydantic_html_validator)]
SafePlainTextString = Annotated[str, BeforeValidator(_pydantic_plain_text_validator)]