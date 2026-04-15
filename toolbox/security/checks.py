# toolbox/security/checks.py

def is_debug_enabled(settings_obj) -> bool:
    return bool(getattr(settings_obj, "DEBUG", False))


def has_secret_key(settings_obj) -> bool:
    return bool(getattr(settings_obj, "SECRET_KEY", ""))


def has_allowed_hosts(settings_obj) -> bool:
    return bool(getattr(settings_obj, "ALLOWED_HOSTS", []))