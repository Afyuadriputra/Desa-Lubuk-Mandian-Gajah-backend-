# features/dashboard_admin/permissions.py

from toolbox.security.auth import is_active_user

def can_view_dashboard(actor) -> bool:
    """Hanya Admin dan Super Admin (is_staff) yang bisa melihat dashboard analitik."""
    return is_active_user(actor) and getattr(actor, 'is_staff', False)