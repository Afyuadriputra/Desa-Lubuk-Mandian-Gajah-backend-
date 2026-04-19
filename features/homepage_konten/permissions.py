from toolbox.security.auth import is_internal_admin


def can_manage_homepage_content(actor) -> bool:
    return bool(actor and getattr(actor, "is_authenticated", False) and is_internal_admin(actor))

