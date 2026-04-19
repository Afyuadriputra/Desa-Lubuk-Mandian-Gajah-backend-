from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone

from features.dashboard_admin.domain import DashboardAccessError
from features.dashboard_admin.services import DashboardService
from features.homepage_konten.models import HomepageContent, HomepageCultureCard, HomepageStatisticItem
from features.layanan_administrasi.models import LayananSurat, LayananSuratStatusHistory
from features.pengaduan_warga.models import LayananPengaduan, LayananPengaduanHistory
from features.potensi_ekonomi.models import BumdesUnitUsaha
from features.profil_wilayah.models import ProfilDesa, WilayahDusun, WilayahPerangkat
from features.publikasi_informasi.models import Publikasi

User = get_user_model()


@pytest.fixture(autouse=True)
def clear_dashboard_cache():
    cache.clear()


@pytest.fixture
def admin_desa(db):
    return User.objects.create_user(
        nik="3333333333333333",
        password="pass12345",
        nama_lengkap="Admin Desa",
        role="ADMIN",
        is_staff=True,
    )


@pytest.fixture
def dashboard_seed(db, admin_desa, warga_user):
    now = timezone.now()
    warga2 = User.objects.create_user(
        nik="2222222222222222",
        password="pass12345",
        nama_lengkap="Warga Kedua",
        role="WARGA",
    )
    User.objects.create_user(
        nik="5555555555555555",
        password="pass12345",
        nama_lengkap="BUMDes User",
        role="BUMDES",
        is_staff=True,
    )
    inactive_user = User.objects.create_user(
        nik="6666666666666666",
        password="pass12345",
        nama_lengkap="Warga Nonaktif",
        role="WARGA",
        is_active=False,
    )
    inactive_user.updated_at = now - timedelta(hours=2)
    inactive_user.save(update_fields=["updated_at"])

    pending_old = LayananSurat.objects.create(pemohon=warga_user, jenis_surat="SKU", keperluan="Untuk usaha toko kelontong", status="PENDING")
    verified_warning = LayananSurat.objects.create(pemohon=warga_user, jenis_surat="SKTM", keperluan="Pengajuan bantuan pendidikan", status="VERIFIED")
    processed_recent = LayananSurat.objects.create(pemohon=warga2, jenis_surat="DOMISILI", keperluan="Administrasi tempat tinggal tetap", status="PROCESSED", nomor_surat="470/01")
    done_surat = LayananSurat.objects.create(pemohon=warga_user, jenis_surat="SKU", keperluan="Pengajuan surat selesai lengkap", status="DONE", nomor_surat="470/02")
    rejected_surat = LayananSurat.objects.create(
        pemohon=warga2,
        jenis_surat="SKTM",
        keperluan="Permohonan bantuan sosial keluarga",
        status="REJECTED",
        rejection_reason="Dokumen belum lengkap",
    )

    LayananSurat.objects.filter(id=pending_old.id).update(created_at=now - timedelta(hours=80), updated_at=now - timedelta(hours=80))
    LayananSurat.objects.filter(id=verified_warning.id).update(created_at=now - timedelta(hours=30), updated_at=now - timedelta(hours=30))
    LayananSurat.objects.filter(id=processed_recent.id).update(created_at=now - timedelta(hours=6), updated_at=now - timedelta(hours=6))
    LayananSurat.objects.filter(id=done_surat.id).update(created_at=now - timedelta(hours=10), updated_at=now - timedelta(hours=1))
    LayananSurat.objects.filter(id=rejected_surat.id).update(created_at=now - timedelta(hours=12), updated_at=now - timedelta(hours=1))

    pending_old.refresh_from_db()
    verified_warning.refresh_from_db()
    processed_recent.refresh_from_db()
    done_surat.refresh_from_db()
    rejected_surat.refresh_from_db()

    LayananSuratStatusHistory.objects.create(
        surat=done_surat,
        status_from="PROCESSED",
        status_to="DONE",
        changed_by=admin_desa,
        notes="PDF selesai dibuat",
        created_at=now - timedelta(hours=1),
    )

    open_old = LayananPengaduan.objects.create(
        pelapor=warga_user,
        kategori="Infrastruktur",
        judul="Jalan utama rusak berat",
        deskripsi="Banyak lubang besar dan membahayakan pengendara.",
        status="OPEN",
    )
    triaged_warning = LayananPengaduan.objects.create(
        pelapor=warga2,
        kategori="Pelayanan",
        judul="Pelayanan lambat di kantor desa",
        deskripsi="Antrian lama dan informasi kurang jelas dari petugas.",
        status="TRIAGED",
    )
    resolved_pengaduan = LayananPengaduan.objects.create(
        pelapor=warga_user,
        kategori="Lingkungan",
        judul="Sampah menumpuk di area pasar",
        deskripsi="Perlu pengangkutan rutin agar tidak bau.",
        status="RESOLVED",
    )
    closed_pengaduan = LayananPengaduan.objects.create(
        pelapor=warga2,
        kategori="Infrastruktur",
        judul="Lampu jalan mati",
        deskripsi="Sudah diperbaiki kemarin sore.",
        status="CLOSED",
    )

    LayananPengaduan.objects.filter(id=open_old.id).update(created_at=now - timedelta(hours=90), updated_at=now - timedelta(hours=90))
    LayananPengaduan.objects.filter(id=triaged_warning.id).update(created_at=now - timedelta(hours=28), updated_at=now - timedelta(hours=10))
    LayananPengaduan.objects.filter(id=resolved_pengaduan.id).update(created_at=now - timedelta(hours=40), updated_at=now - timedelta(hours=2))
    LayananPengaduan.objects.filter(id=closed_pengaduan.id).update(created_at=now - timedelta(hours=14), updated_at=now - timedelta(hours=3))

    open_old.refresh_from_db()
    triaged_warning.refresh_from_db()
    resolved_pengaduan.refresh_from_db()
    closed_pengaduan.refresh_from_db()

    LayananPengaduanHistory.objects.create(
        pengaduan=triaged_warning,
        status_from="OPEN",
        status_to="TRIAGED",
        changed_by=admin_desa,
        notes="Masuk antrian pemeriksaan",
        created_at=now - timedelta(hours=10),
    )
    LayananPengaduanHistory.objects.create(
        pengaduan=resolved_pengaduan,
        status_from="IN_PROGRESS",
        status_to="RESOLVED",
        changed_by=admin_desa,
        notes="Sudah ditindaklanjuti",
        created_at=now - timedelta(hours=2),
    )

    draft = Publikasi.objects.create(
        judul="Rencana kerja bakti dusun barat",
        konten_html="<p>Draft kerja bakti</p>",
        jenis="PENGUMUMAN",
        penulis=admin_desa,
        status="DRAFT",
    )
    published = Publikasi.objects.create(
        judul="Berita panen raya desa",
        konten_html="<p>Panen raya berjalan sukses</p>",
        jenis="BERITA",
        penulis=admin_desa,
        status="PUBLISHED",
        published_at=now - timedelta(minutes=30),
    )
    Publikasi.objects.filter(id=draft.id).update(created_at=now - timedelta(days=3), updated_at=now - timedelta(days=2))
    Publikasi.objects.filter(id=published.id).update(created_at=now - timedelta(days=1), updated_at=now - timedelta(minutes=30))

    BumdesUnitUsaha.objects.create(
        nama_usaha="Wisata Embung Desa",
        kategori="WISATA",
        deskripsi="Destinasi wisata keluarga",
        is_published=True,
    )
    BumdesUnitUsaha.objects.create(
        nama_usaha="Koperasi Makmur",
        kategori="KOPERASI",
        deskripsi="Masih disiapkan",
        is_published=False,
    )

    WilayahDusun.objects.create(nama_dusun="Dusun Barat", kepala_dusun="Pak Budi")
    WilayahDusun.objects.create(nama_dusun="Dusun Timur", kepala_dusun="Bu Sari")
    WilayahPerangkat.objects.create(user=admin_desa, jabatan="Sekretaris Desa", is_published=True)
    WilayahPerangkat.objects.create(user=warga2, jabatan="Staf Pelayanan", is_published=False)
    ProfilDesa.objects.create(visi="Desa maju", misi="Pelayanan cepat", sejarah="")
    homepage = HomepageContent.objects.create(
        id=1,
        tagline="Tagline desa",
        hero_image="https://example.com/hero.jpg",
        hero_badge="Badge",
        village_name="Desa Lubuk Mandian Gajah",
        hero_description="Deskripsi hero desa yang cukup panjang.",
        contact_address="Jl. Desa",
        contact_whatsapp="08123456789",
        naming_title="Asal nama",
        footer_description="Footer desa",
    )
    HomepageCultureCard.objects.create(
        homepage=homepage,
        icon="groups",
        title="Budaya",
        description="Deskripsi budaya",
        sort_order=1,
    )
    HomepageStatisticItem.objects.create(
        homepage=homepage,
        label="RW",
        value="4",
        sort_order=1,
    )

    return {
        "pending_old": pending_old,
        "verified_warning": verified_warning,
        "processed_recent": processed_recent,
        "done_surat": done_surat,
        "open_old": open_old,
        "triaged_warning": triaged_warning,
        "resolved_pengaduan": resolved_pengaduan,
    }


@pytest.mark.django_db
class TestDashboardPermissions:
    def test_warga_tidak_bisa_melihat_dashboard(self, warga_user):
        service = DashboardService()
        with pytest.raises(DashboardAccessError):
            service.get_overview(actor=warga_user)

    def test_admin_desa_bisa_melihat_dashboard(self, admin_desa, dashboard_seed):
        data = DashboardService().get_overview(actor=admin_desa)
        assert "summary" in data["data"]


@pytest.mark.django_db
class TestDashboardOverview:
    def test_overview_summary_alerts_quick_actions(self, admin_desa, dashboard_seed):
        data = DashboardService().get_overview(actor=admin_desa)["data"]

        assert data["summary"]["surat_pending"] == 1
        assert data["summary"]["surat_verified"] == 1
        assert data["summary"]["surat_processed"] == 1
        assert data["summary"]["surat_done"] == 1
        assert data["summary"]["surat_rejected"] == 1
        assert data["summary"]["pengaduan_aktif"] == 2
        assert data["summary"]["pengaduan_selesai"] == 2
        assert data["summary"]["total_warga_aktif"] == 2
        assert data["summary"]["total_unit_published"] == 1
        assert any(item["severity"] == "critical" for item in data["alerts"])
        assert any(action["key"] == "surat-pending" for action in data["quick_actions"])
        assert any(action["key"] == "kelola-homepage" for action in data["quick_actions"])
        assert any(flag["key"] == "homepage-content" for flag in data["health"]["content_flags"])

    def test_empty_shape_tetap_konsisten(self, admin_desa):
        data = DashboardService().get_overview(actor=admin_desa)["data"]
        assert data["summary"]["surat_pending"] == 0
        assert isinstance(data["alerts"], list)
        assert isinstance(data["charts"]["surat_by_status"], list)
        assert isinstance(data["health"]["content_flags"], list)


@pytest.mark.django_db
class TestDashboardQueues:
    def test_surat_queue_filter_status_dan_aging(self, admin_desa, dashboard_seed):
        data = DashboardService().get_surat_queue(
            actor=admin_desa,
            filters={"scope": "all", "status": "PENDING", "aging": "overdue"},
        )
        assert data["meta"]["total"] == 1
        assert data["data"][0]["id"] == str(dashboard_seed["pending_old"].id)
        assert data["data"][0]["aging_bucket"] == "overdue"

    def test_pengaduan_queue_scope_week_memuat_item_yang_relevan(self, admin_desa, dashboard_seed):
        data = DashboardService().get_pengaduan_queue(actor=admin_desa, filters={"scope": "week"})
        ids = {item["id"] for item in data["data"]}
        assert str(dashboard_seed["open_old"].id) in ids
        assert str(dashboard_seed["triaged_warning"].id) in ids
        assert data["meta"]["scope"] == "week"


@pytest.mark.django_db
class TestDashboardAnalytics:
    def test_recent_activity_merge_dan_sorting_desc(self, admin_desa, dashboard_seed):
        data = DashboardService().get_recent_activity(actor=admin_desa, limit=8)["data"]
        timestamps = [item["created_at"] for item in data]
        assert timestamps == sorted(timestamps, reverse=True)
        assert {"surat", "pengaduan", "publikasi", "auth", "homepage"} & {item["module"] for item in data}


@pytest.mark.django_db
class TestDashboardHomepageHealth:
    def test_content_health_memuat_ringkasan_homepage(self, admin_desa, dashboard_seed):
        data = DashboardService().get_content_health(actor=admin_desa)["data"]

        assert "homepage_filled_sections" in data["summary"]
        assert "homepage_empty_sections" in data["summary"]
        assert "homepage_completeness_score" in data["summary"]
        assert "homepage_important_missing" in data["summary"]
        assert "homepage_list_counts" in data["summary"]
        assert data["summary"]["homepage_list_counts"]["culture_cards"] == 1
        assert data["summary"]["homepage_list_counts"]["stats_items"] == 1
        assert data["summary"]["homepage_completeness_score"] > 0

    def test_overview_memuat_alert_homepage_jika_section_penting_kosong(self, admin_desa):
        data = DashboardService().get_overview(actor=admin_desa)["data"]
        flags = {item["key"]: item for item in data["health"]["content_flags"]}
        alerts = {item["key"]: item for item in data["alerts"]}

        assert "homepage-important-missing" in flags
        assert flags["homepage-important-missing"]["severity"] == "critical"
        assert "homepage-missing-important" in alerts

    def test_surat_analytics_berisi_summary_trend_dan_missing_documents(self, admin_desa, dashboard_seed):
        data = DashboardService().get_surat_analytics(actor=admin_desa, period_days=7)["data"]
        assert data["summary"]["average_completion_hours"] > 0
        assert data["summary"]["missing_document_total"] >= 1
        assert any(item["label"] == "SKU" for item in data["by_jenis"])
        assert isinstance(data["trend"], list)

    def test_pengaduan_analytics_berisi_response_metrics(self, admin_desa, dashboard_seed):
        data = DashboardService().get_pengaduan_analytics(actor=admin_desa, period_days=7)["data"]
        assert data["summary"]["average_first_response_hours"] > 0
        assert data["summary"]["average_resolved_hours"] > 0
        assert data["oldest_active"][0]["id"] == str(dashboard_seed["open_old"].id)


@pytest.mark.django_db
class TestDashboardHealth:
    def test_content_health_menghitung_draft_dan_unpublished(self, admin_desa, dashboard_seed):
        data = DashboardService().get_content_health(actor=admin_desa)["data"]
        assert data["summary"]["draft_publications"] == 1
        assert data["summary"]["unpublished_units"] == 1
        assert data["summary"]["unpublished_perangkat"] == 1

    def test_master_health_menghitung_profil_dan_role_counts(self, admin_desa, dashboard_seed):
        data = DashboardService().get_master_health(actor=admin_desa)["data"]
        assert data["summary"]["dusun_total"] == 2
        assert data["summary"]["perangkat_published"] == 1
        assert data["summary"]["profile_completeness"]["score"] == 66
        role_counts = {item["role"]: item["total"] for item in data["summary"]["role_counts"]}
        assert role_counts["ADMIN"] == 1
        assert role_counts["WARGA"] == 3
