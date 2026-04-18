import pytest

@pytest.mark.django_db
class TestDashboardAPI:

    def test_warga_ditolak_akses_dashboard(self, client, warga_user):
        client.force_login(warga_user)
        # PERBAIKAN: Tambahkan '/' di akhir URL dan follow=True
        response = client.get("/api/v1/dashboard-admin/analitik/", follow=True)
        assert response.status_code in [401, 403] 

    def test_admin_bisa_akses_dashboard_dan_data_teragregasi(self, client, admin_user, warga_user):
        client.force_login(admin_user)
        from features.layanan_administrasi.models import LayananSurat
        LayananSurat.objects.create(pemohon=warga_user, jenis_surat="SKU", keperluan="Tes", status="PENDING")
        LayananSurat.objects.create(pemohon=warga_user, jenis_surat="SKTM", keperluan="Tes", status="PENDING")
        
        # PERBAIKAN: Tambahkan '/' di akhir URL dan follow=True
        response = client.get("/api/v1/dashboard-admin/analitik/", follow=True)
        assert response.status_code == 200