import pytest
from django.core.cache import cache
from django.urls import reverse

from features.dashboard_admin.tests.test_dashboard import admin_desa, dashboard_seed


@pytest.fixture(autouse=True)
def clear_dashboard_cache():
    cache.clear()


@pytest.mark.django_db
class TestDashboardAPI:
    def test_named_routes_bisa_di_reverse(self):
        route_names = [
            "dashboard-overview",
            "dashboard-surat-queue",
            "dashboard-pengaduan-queue",
            "dashboard-recent-activity",
            "dashboard-surat-analytics",
            "dashboard-pengaduan-analytics",
            "dashboard-content-health",
            "dashboard-master-health",
        ]
        for name in route_names:
            assert reverse(name)

    def test_warga_ditolak_akses_dashboard(self, client, warga_user):
        client.force_login(warga_user)
        response = client.get(reverse("dashboard-overview"), follow=True)
        assert response.status_code in {401, 403}

    def test_admin_bisa_akses_overview(self, client, admin_desa, dashboard_seed):
        client.force_login(admin_desa)
        response = client.get(reverse("dashboard-overview"))
        assert response.status_code == 200
        payload = response.json()["data"]
        assert "summary" in payload
        assert "alerts" in payload
        assert "health" in payload
        assert "quick_actions" in payload

    def test_queue_invalid_scope_return_400(self, client, admin_desa, dashboard_seed):
        client.force_login(admin_desa)
        response = client.get(reverse("dashboard-surat-queue"), {"scope": "bulan"})
        assert response.status_code == 400

    def test_recent_activity_dan_health_endpoint_berjalan(self, client, admin_desa, dashboard_seed):
        client.force_login(admin_desa)

        recent = client.get(reverse("dashboard-recent-activity"), {"limit": 5})
        content = client.get(reverse("dashboard-content-health"))
        master = client.get(reverse("dashboard-master-health"))

        assert recent.status_code == 200
        assert content.status_code == 200
        assert master.status_code == 200
        assert isinstance(recent.json()["data"], list)
        assert "summary" in content.json()["data"]
        assert "summary" in master.json()["data"]

    def test_legacy_endpoint_tetap_kompatibel(self, client, admin_desa, dashboard_seed):
        client.force_login(admin_desa)
        response = client.get("/api/v1/dashboard-admin/analitik/")
        assert response.status_code == 200
        payload = response.json()["data"]
        assert "summary" in payload
        assert "charts" in payload
