# Feature Context: dashboard_admin

Generated at: 2026-04-18T23:18:05
Feature path: `D:\Kuliah\joki\radit\desa\backend\features\dashboard_admin`

Dokumen ini berisi layer penting untuk konteks LLM.
Folder `tests`, `migrations`, `logs`, dan file non-konteks tidak disertakan.

## Included Layers

- `apps.py`
- `models.py`
- `domain.py`
- `repositories.py`
- `services.py`
- `permissions.py`
- `schemas.py`
- `api.py`

---

## File: `apps.py`

```python
# features/dashboard_admin/apps.py

from django.apps import AppConfig

class DashboardAdminConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "features.dashboard_admin"
```

---

## File: `models.py`

```python
# features/dashboard_admin/models.py

# YAGNI: Modul Dashboard hanya melakukan agregasi data dari modul lain.
# Tidak ada tabel database baru yang diperlukan di sini.
```

---

## File: `domain.py`

```python
# features/dashboard_admin/domain.py

class DashboardError(Exception):
    """Base exception untuk modul dashboard."""

class DashboardAccessError(DashboardError):
    """Akses ditolak untuk melihat analitik dashboard."""
```

---

## File: `repositories.py`

```python
# features/dashboard_admin/repositories.py

from django.db.models import Count
from django.contrib.auth import get_user_model

from features.layanan_administrasi.models import LayananSurat
from features.pengaduan_warga.models import LayananPengaduan
from features.potensi_ekonomi.models import BumdesUnitUsaha

User = get_user_model()

class DashboardRepository:
    def get_summary_metrics(self) -> dict:
        return {
            "total_warga_aktif": User.objects.filter(role="WARGA", is_active=True).count(),
            "surat_pending": LayananSurat.objects.filter(status="PENDING").count(),
            "pengaduan_aktif": LayananPengaduan.objects.filter(status__in=["OPEN", "TRIAGED", "IN_PROGRESS"]).count(),
            "bumdes_published": BumdesUnitUsaha.objects.filter(is_published=True).count()
        }

    def get_surat_stats_by_status(self) -> list:
        # Menghasilkan: [{'status': 'PENDING', 'total': 10}, {'status': 'DONE', 'total': 45}]
        return list(LayananSurat.objects.values('status').annotate(total=Count('id')).order_by('-total'))

    def get_pengaduan_stats_by_kategori(self) -> list:
        # Menghasilkan: [{'kategori': 'Infrastruktur', 'total': 20}, ...]
        return list(LayananPengaduan.objects.values('kategori').annotate(total=Count('id')).order_by('-total'))
```

---

## File: `services.py`

```python
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
```

---

## File: `permissions.py`

```python
# features/dashboard_admin/permissions.py

from toolbox.security.auth import is_active_user

def can_view_dashboard(actor) -> bool:
    """Hanya Admin dan Super Admin (is_staff) yang bisa melihat dashboard analitik."""
    return is_active_user(actor) and getattr(actor, 'is_staff', False)
```

---

## File: `schemas.py`

```python
# features/dashboard_admin/schemas.py
from ninja import Schema
from typing import List, Dict, Any

class SummarySchema(Schema):
    total_warga_aktif: int
    surat_pending: int
    pengaduan_aktif: int
    bumdes_published: int

class StatItemSchema(Schema):
    # Field opsional karena key-nya bisa 'status' atau 'kategori'
    status: str = None
    kategori: str = None
    total: int

class DashboardChartSchema(Schema):
    surat_by_status: List[StatItemSchema]
    pengaduan_by_kategori: List[StatItemSchema]

class DashboardResponseSchema(Schema):
    data: Dict[str, Any] # Membungkus response dalam key "data"
```

---

## File: `api.py`

```python
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
```

---
