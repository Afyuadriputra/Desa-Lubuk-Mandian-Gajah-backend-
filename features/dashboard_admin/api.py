# features/dashboard_admin/api.py
from ninja import Router
from django.http import HttpRequest
from features.dashboard_admin.services import DashboardService
from features.dashboard_admin.domain import DashboardAccessError
from toolbox.security.auth import is_active_user

# Membuat router untuk dashboard (Bisa dikelompokkan dengan tag di Swagger)
router = Router(tags=["Dashboard Analitik"])
dashboard_service = DashboardService()

# 1. Tidak perlu @require_GET, langsung pakai router.get()
# 2. Response schema langsung ditentukan agar validasinya otomatis
@router.get("/analitik/", response={200: dict, 401: dict, 403: dict, 500: dict})
def analitik_dashboard_api(request: HttpRequest):
    actor = getattr(request, "user", None)
    
    # Validasi Autentikasi
    if not is_active_user(actor):
        return 401, {"detail": "Unauthorized."}
    
    try:
        # Panggil service yang tidak berubah sama sekali
        data = dashboard_service.get_analitik_lengkap(actor)
        return 200, {"data": data}
    
    except DashboardAccessError as e:
        return 403, {"detail": str(e)}
    except Exception as e:
        return 500, {"detail": "Terjadi kesalahan pada server saat memuat analitik."}