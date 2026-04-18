from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Min, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from features.layanan_administrasi.models import LayananSurat, LayananSuratStatusHistory
from features.pengaduan_warga.models import LayananPengaduan, LayananPengaduanHistory
from features.potensi_ekonomi.models import BumdesUnitUsaha
from features.profil_wilayah.models import ProfilDesa, WilayahDusun, WilayahPerangkat
from features.publikasi_informasi.models import Publikasi

User = get_user_model()


class DashboardRepository:
    def get_summary_metrics(self) -> dict:
        surat_counts = {
            item["status"]: item["total"]
            for item in LayananSurat.objects.values("status").annotate(total=Count("id"))
        }
        pengaduan_counts = {
            item["status"]: item["total"]
            for item in LayananPengaduan.objects.values("status").annotate(total=Count("id"))
        }

        today = timezone.localdate()
        return {
            "total_pengajuan_surat_hari_ini": LayananSurat.objects.filter(created_at__date=today).count(),
            "surat_pending": surat_counts.get("PENDING", 0),
            "surat_verified": surat_counts.get("VERIFIED", 0),
            "surat_processed": surat_counts.get("PROCESSED", 0),
            "surat_done": surat_counts.get("DONE", 0),
            "surat_rejected": surat_counts.get("REJECTED", 0),
            "pengaduan_aktif": sum(pengaduan_counts.get(status, 0) for status in ["OPEN", "TRIAGED", "IN_PROGRESS"]),
            "pengaduan_selesai": sum(pengaduan_counts.get(status, 0) for status in ["RESOLVED", "CLOSED"]),
            "total_warga_aktif": User.objects.filter(role="WARGA", is_active=True).count(),
            "total_unit_published": BumdesUnitUsaha.objects.filter(is_published=True).count(),
        }

    def get_surat_stats_by_status(self) -> list[dict]:
        return [
            {"label": item["status"], "total": item["total"]}
            for item in LayananSurat.objects.values("status").annotate(total=Count("id")).order_by("-total", "status")
        ]

    def get_surat_stats_by_jenis(self) -> list[dict]:
        return [
            {"label": item["jenis_surat"], "total": item["total"]}
            for item in LayananSurat.objects.values("jenis_surat").annotate(total=Count("id")).order_by("-total", "jenis_surat")
        ]

    def get_pengaduan_stats_by_status(self) -> list[dict]:
        return [
            {"label": item["status"], "total": item["total"]}
            for item in LayananPengaduan.objects.values("status").annotate(total=Count("id")).order_by("-total", "status")
        ]

    def get_pengaduan_stats_by_kategori(self) -> list[dict]:
        return [
            {"label": item["kategori"], "total": item["total"]}
            for item in LayananPengaduan.objects.values("kategori").annotate(total=Count("id")).order_by("-total", "kategori")
        ]

    def get_surat_trend(self, days: int = 7) -> list[dict]:
        start = timezone.now() - timedelta(days=days - 1)
        return list(
            LayananSurat.objects.filter(created_at__gte=start)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(total=Count("id"))
            .order_by("day")
        )

    def get_pengaduan_trend(self, days: int = 7) -> list[dict]:
        start = timezone.now() - timedelta(days=days - 1)
        return list(
            LayananPengaduan.objects.filter(created_at__gte=start)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(total=Count("id"))
            .order_by("day")
        )

    def get_surat_queue_queryset(self):
        return LayananSurat.objects.select_related("pemohon").all()

    def get_pengaduan_queue_queryset(self):
        return LayananPengaduan.objects.select_related("pelapor").all()

    def get_surat_histories(self, limit: int):
        return list(
            LayananSuratStatusHistory.objects.select_related("surat", "changed_by", "surat__pemohon")
            .order_by("-created_at")[:limit]
        )

    def get_pengaduan_histories(self, limit: int):
        return list(
            LayananPengaduanHistory.objects.select_related("pengaduan", "changed_by", "pengaduan__pelapor")
            .order_by("-created_at")[:limit]
        )

    def get_recent_publications(self, limit: int):
        return list(Publikasi.objects.select_related("penulis").order_by("-updated_at")[:limit])

    def get_recent_users(self, limit: int):
        return list(User.objects.order_by("-updated_at")[:limit])

    def get_surat_completion_candidates(self):
        return list(
            LayananSurat.objects.filter(status="DONE")
            .annotate(done_at=Min("histori_status__created_at", filter=Q(histori_status__status_to="DONE")))
            .filter(done_at__isnull=False)
        )

    def get_surat_rejection_stats(self) -> list[dict]:
        data = (
            LayananSurat.objects.filter(status="REJECTED")
            .exclude(rejection_reason__isnull=True)
            .exclude(rejection_reason__exact="")
            .values("rejection_reason")
            .annotate(total=Count("id"))
            .order_by("-total", "rejection_reason")
        )
        return [
            {"reason": item["rejection_reason"], "total": item["total"]}
            for item in data
        ]

    def get_surat_missing_documents(self) -> list:
        return list(
            LayananSurat.objects.select_related("pemohon")
            .filter(
                Q(status__in=["PROCESSED", "DONE"])
                & (
                    Q(nomor_surat__isnull=True)
                    | Q(nomor_surat="")
                    | Q(pdf_file__isnull=True)
                    | Q(pdf_file="")
                )
            )
            .order_by("-updated_at")
        )

    def get_pengaduan_response_candidates(self):
        return list(
            LayananPengaduan.objects.filter(status__in=["TRIAGED", "IN_PROGRESS", "RESOLVED", "CLOSED"])
            .annotate(
                first_response_at=Min(
                    "histori_tindak_lanjut__created_at",
                    filter=Q(histori_tindak_lanjut__status_to__in=["TRIAGED", "IN_PROGRESS", "RESOLVED", "CLOSED"]),
                ),
                resolved_at=Min(
                    "histori_tindak_lanjut__created_at",
                    filter=Q(histori_tindak_lanjut__status_to="RESOLVED"),
                ),
            )
        )

    def get_oldest_active_pengaduan(self):
        return list(
            LayananPengaduan.objects.select_related("pelapor")
            .filter(status__in=["OPEN", "TRIAGED", "IN_PROGRESS"])
            .order_by("created_at")[:5]
        )

    def get_draft_publications(self):
        return list(Publikasi.objects.filter(status="DRAFT").order_by("created_at"))

    def get_published_publications_count(self) -> int:
        return Publikasi.objects.filter(status="PUBLISHED").count()

    def get_unpublished_units(self):
        return list(BumdesUnitUsaha.objects.filter(is_published=False).order_by("created_at"))

    def get_unpublished_perangkat(self):
        return list(WilayahPerangkat.objects.select_related("user").filter(is_published=False).order_by("created_at"))

    def get_published_perangkat_count(self) -> int:
        return WilayahPerangkat.objects.filter(is_published=True).count()

    def get_total_perangkat_count(self) -> int:
        return WilayahPerangkat.objects.count()

    def get_total_dusun_count(self) -> int:
        return WilayahDusun.objects.count()

    def get_profile(self):
        return ProfilDesa.objects.first()

    def get_user_role_counts(self) -> list[dict]:
        return list(User.objects.values("role").annotate(total=Count("id")).order_by("role"))

    def get_user_status_counts(self) -> dict:
        return {
            "active": User.objects.filter(is_active=True).count(),
            "inactive": User.objects.filter(is_active=False).count(),
        }
