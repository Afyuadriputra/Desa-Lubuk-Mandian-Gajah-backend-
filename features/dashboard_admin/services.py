# features/dashboard_admin/services.py

from features.dashboard_admin.domain import DashboardAccessError
from features.dashboard_admin.permissions import can_view_dashboard
from features.dashboard_admin.repositories import DashboardRepository
from toolbox.logging import get_logger

class DashboardService:
    def __init__(self, repo: DashboardRepository = None):
        # Dependency Inversion Principle
        self.repo = repo or DashboardRepository()
        self.logger = get_logger("features.dashboard_admin.services")

    def get_analitik_lengkap(self, actor) -> dict:
        if not can_view_dashboard(actor):
            self.logger.warning("Akses dashboard ditolak untuk user_id={user_id}", user_id=actor.id)
            raise DashboardAccessError("Anda tidak memiliki hak akses ke Dashboard Admin.")

        # Merakit semua data dari repository
        summary = self.repo.get_summary_metrics()
        surat_stats = self.repo.get_surat_stats_by_status()
        pengaduan_stats = self.repo.get_pengaduan_stats_by_kategori()

        self.logger.info("Data analitik dashboard berhasil ditarik oleh user_id={user_id}", user_id=actor.id)

        return {
            "summary": summary,
            "charts": {
                "surat_by_status": surat_stats,
                "pengaduan_by_kategori": pengaduan_stats
            }
        }