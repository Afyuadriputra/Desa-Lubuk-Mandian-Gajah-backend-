import re

from toolbox.security.sanitizers import sanitize_plain_text


class HomepageKontenError(Exception):
    """Base exception untuk feature homepage konten."""


class HomepageKontenAccessError(HomepageKontenError):
    """Akses ditolak."""


class HomepageKontenNotFoundError(HomepageKontenError):
    """Data tidak ditemukan."""


def validate_required_text(value: str | None, field_name: str, min_length: int = 3) -> str:
    normalized = _sanitize_strict_plain_text(value)
    if len(normalized) < min_length:
        raise HomepageKontenError(f"{field_name} minimal {min_length} karakter.")
    return normalized


def validate_optional_text(value: str | None) -> str:
    return _sanitize_strict_plain_text(value)


def validate_sort_order(sort_order: int) -> int:
    if sort_order < 0:
        raise HomepageKontenError("sort_order tidak boleh negatif.")
    return sort_order


def validate_json_string_list(items, field_name: str) -> list[str]:
    if items is None:
        return []
    if not isinstance(items, list):
        raise HomepageKontenError(f"{field_name} harus berupa list.")
    return [sanitize_plain_text(str(item)) for item in items if sanitize_plain_text(str(item))]


def validate_office_hours(items) -> list[dict]:
    if items is None:
        return []
    if not isinstance(items, list):
        raise HomepageKontenError("officeHours harus berupa list.")

    normalized = []
    for item in items:
        if not isinstance(item, dict):
            raise HomepageKontenError("Item officeHours harus berupa object.")
        day = validate_required_text(item.get("day"), "Hari officeHours", min_length=2)
        time = validate_required_text(item.get("time"), "Waktu officeHours", min_length=2)
        normalized.append(
            {
                "day": day,
                "time": time,
                "danger": bool(item.get("danger", False)),
            }
        )
    return normalized


def _sanitize_strict_plain_text(value: str | None) -> str:
    if not value:
        return ""
    without_script = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", value, flags=re.IGNORECASE | re.DOTALL)
    return sanitize_plain_text(without_script)
