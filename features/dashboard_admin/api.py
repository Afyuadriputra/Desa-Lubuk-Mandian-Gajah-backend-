from ninja import Router

from features.dashboard_admin.domain import DashboardAccessError, DashboardValidationError
from features.dashboard_admin.schemas import (
    DashboardAnalyticsResponseSchema,
    DashboardHealthResponseSchema,
    DashboardOverviewResponseSchema,
    LegacyDashboardResponseSchema,
    QueueResponseSchema,
    RecentActivityResponseSchema,
)
from features.dashboard_admin.services import DashboardService
from toolbox.api.auth import AuthAdminOnly

router = Router(tags=["Dashboard Analitik"])
dashboard_service = DashboardService()


def _filters(scope: str = "all", status: str | None = None, aging: str | None = None) -> dict:
    return {"scope": scope, "status": status, "aging": aging}


@router.get("/overview", auth=AuthAdminOnly, response={200: DashboardOverviewResponseSchema, 403: dict}, url_name="dashboard-overview")
def overview_dashboard_api(request):
    try:
        return 200, dashboard_service.get_overview(request.user)
    except DashboardAccessError as exc:
        return 403, {"detail": str(exc)}


@router.get("/surat-queue", auth=AuthAdminOnly, response={200: QueueResponseSchema, 400: dict, 403: dict}, url_name="dashboard-surat-queue")
def surat_queue_dashboard_api(request, scope: str = "all", status: str | None = None, aging: str | None = None):
    try:
        return 200, dashboard_service.get_surat_queue(request.user, _filters(scope, status, aging))
    except DashboardValidationError as exc:
        return 400, {"detail": str(exc)}
    except DashboardAccessError as exc:
        return 403, {"detail": str(exc)}


@router.get("/pengaduan-queue", auth=AuthAdminOnly, response={200: QueueResponseSchema, 400: dict, 403: dict}, url_name="dashboard-pengaduan-queue")
def pengaduan_queue_dashboard_api(request, scope: str = "all", status: str | None = None, aging: str | None = None):
    try:
        return 200, dashboard_service.get_pengaduan_queue(request.user, _filters(scope, status, aging))
    except DashboardValidationError as exc:
        return 400, {"detail": str(exc)}
    except DashboardAccessError as exc:
        return 403, {"detail": str(exc)}


@router.get("/recent-activity", auth=AuthAdminOnly, response={200: RecentActivityResponseSchema, 403: dict}, url_name="dashboard-recent-activity")
def recent_activity_dashboard_api(request, limit: int = 10):
    try:
        return 200, dashboard_service.get_recent_activity(request.user, limit=limit)
    except DashboardAccessError as exc:
        return 403, {"detail": str(exc)}


@router.get("/surat-analytics", auth=AuthAdminOnly, response={200: DashboardAnalyticsResponseSchema, 403: dict}, url_name="dashboard-surat-analytics")
def surat_analytics_dashboard_api(request, period_days: int = 7):
    try:
        return 200, dashboard_service.get_surat_analytics(request.user, period_days=period_days)
    except DashboardAccessError as exc:
        return 403, {"detail": str(exc)}


@router.get("/pengaduan-analytics", auth=AuthAdminOnly, response={200: DashboardAnalyticsResponseSchema, 403: dict}, url_name="dashboard-pengaduan-analytics")
def pengaduan_analytics_dashboard_api(request, period_days: int = 7):
    try:
        return 200, dashboard_service.get_pengaduan_analytics(request.user, period_days=period_days)
    except DashboardAccessError as exc:
        return 403, {"detail": str(exc)}


@router.get("/content-health", auth=AuthAdminOnly, response={200: DashboardHealthResponseSchema, 403: dict}, url_name="dashboard-content-health")
def content_health_dashboard_api(request):
    try:
        return 200, dashboard_service.get_content_health(request.user)
    except DashboardAccessError as exc:
        return 403, {"detail": str(exc)}


@router.get("/master-health", auth=AuthAdminOnly, response={200: DashboardHealthResponseSchema, 403: dict}, url_name="dashboard-master-health")
def master_health_dashboard_api(request):
    try:
        return 200, dashboard_service.get_master_health(request.user)
    except DashboardAccessError as exc:
        return 403, {"detail": str(exc)}


@router.get("/analitik/", auth=AuthAdminOnly, response={200: LegacyDashboardResponseSchema, 403: dict, 500: dict})
def analitik_dashboard_api(request):
    try:
        return 200, {"data": dashboard_service.get_analitik_lengkap(request.user)}
    except DashboardAccessError as exc:
        return 403, {"detail": str(exc)}
    except Exception:
        return 500, {"detail": "Terjadi kesalahan pada server saat memuat analitik."}
