# toolbox/security/sanitizers.py

import bleach

ALLOWED_TAGS = [
    "p", "br", "strong", "em", "u",
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