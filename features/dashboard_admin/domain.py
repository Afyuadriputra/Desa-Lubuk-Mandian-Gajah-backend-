# features/dashboard_admin/domain.py

class DashboardError(Exception):
    """Base exception untuk modul dashboard."""

class DashboardAccessError(DashboardError):
    """Akses ditolak untuk melihat analitik dashboard."""