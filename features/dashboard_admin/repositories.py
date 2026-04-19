from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Min, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from features.layanan_administrasi.models import LayananSurat, LayananSuratStatusHistory
from features.pengaduan_warga.models import LayananPengaduan, LayananPengaduanHistory
from features.homepage_konten.models import (
    HomepageContent,
    HomepageCultureCard,
    HomepageFacility,
    HomepageFooterLink,
    HomepageGalleryItem,
    HomepagePotentialOpportunityItem,
    HomepageRecoveryItem,
    HomepageStatisticItem,
)
from features.potensi_ekonomi.models import BumdesUnitUsaha
from features.profil_wilayah.models import ProfilDesa, WilayahDusun, WilayahPerangkat
from features.publikasi_informasi.models import Publikasi

User = get_user_model()


class DashboardRepository:
    HOMEPAGE_SCALAR_FIELDS = [
        "tagline",
        "hero_image",
        "hero_badge",
        "brand_logo_url",
        "brand_logo_alt",
        "brand_region_label",
        "village_name",
        "hero_description",
        "contact_address",
        "contact_whatsapp",
        "contact_map_image",
        "quick_stats_description",
        "naming_title",
        "naming_description",
        "naming_image",
        "naming_quote",
        "culture_title",
        "culture_description",
        "sialang_title",
        "sialang_description",
        "sialang_image",
        "sialang_badge",
        "sialang_stat",
        "sialang_quote",
        "peat_title",
        "peat_description",
        "peat_quote",
        "recovery_title",
        "recovery_description",
        "potential_title",
        "potential_quote",
        "potential_opportunities_title",
        "facilities_title",
        "gallery_title",
        "gallery_description",
        "contact_title",
        "contact_description",
        "footer_description",
        "footer_copyright",
    ]
    HOMEPAGE_IMPORTANT_SCALAR_FIELDS = [
        "village_name",
        "tagline",
        "hero_image",
        "hero_description",
        "contact_address",
        "naming_title",
        "culture_title",
        "sialang_title",
        "peat_title",
        "recovery_title",
        "potential_title",
        "facilities_title",
        "gallery_title",
        "contact_title",
        "footer_description",
    ]
    HOMEPAGE_IMPORTANT_LIST_FIELDS = {
        "culture_cards": HomepageCultureCard,
        "facilities": HomepageFacility,
        "gallery": HomepageGalleryItem,
        "footer_links": HomepageFooterLink,
        "stats_items": HomepageStatisticItem,
    }

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

    def get_homepage_content(self) -> HomepageContent:
        content, _ = HomepageContent.objects.get_or_create(id=1)
        return content

    def get_homepage_section_status(self) -> dict:
        content = self.get_homepage_content()
        scalar_filled = sum(1 for field in self.HOMEPAGE_SCALAR_FIELDS if getattr(content, field, ""))
        json_filled = sum(
            1
            for field in ["peat_images", "footer_badges", "office_hours"]
            if getattr(content, field, [])
        )
        list_counts = {
            "culture_cards": HomepageCultureCard.objects.filter(homepage=content).count(),
            "recovery_items": HomepageRecoveryItem.objects.filter(homepage=content).count(),
            "potential_opportunities": HomepagePotentialOpportunityItem.objects.filter(homepage=content).count(),
            "facilities": HomepageFacility.objects.filter(homepage=content).count(),
            "gallery": HomepageGalleryItem.objects.filter(homepage=content).count(),
            "footer_links": HomepageFooterLink.objects.filter(homepage=content).count(),
            "stats_items": HomepageStatisticItem.objects.filter(homepage=content).count(),
        }
        list_filled = sum(1 for total in list_counts.values() if total > 0)
        total_sections = len(self.HOMEPAGE_SCALAR_FIELDS) + 3 + len(list_counts)
        filled_sections = scalar_filled + json_filled + list_filled
        empty_sections = total_sections - filled_sections
        important_missing = [
            field for field in self.HOMEPAGE_IMPORTANT_SCALAR_FIELDS if not getattr(content, field, "")
        ]
        important_missing.extend(
            key for key, model in self.HOMEPAGE_IMPORTANT_LIST_FIELDS.items() if not model.objects.filter(homepage=content).exists()
        )
        completeness_score = round((filled_sections / total_sections) * 100) if total_sections else 0
        return {
            "filled_sections": filled_sections,
            "empty_sections": empty_sections,
            "total_sections": total_sections,
            "list_counts": list_counts,
            "important_missing": important_missing,
            "completeness_score": completeness_score,
        }

    def get_recent_homepage_activity(self, limit: int) -> list[dict]:
        content = self.get_homepage_content()
        items = []
        if content.updated_at:
            items.append(
                {
                    "module": "homepage",
                    "action": "updated",
                    "title": "Konten homepage utama",
                    "created_at": content.updated_at,
                    "target_id": str(content.id),
                    "target_url": "/api/v1/homepage/admin/content",
                }
            )

        child_sources = [
            ("culture card", HomepageCultureCard.objects.filter(homepage=content).order_by("-updated_at")[:limit]),
            ("recovery item", HomepageRecoveryItem.objects.filter(homepage=content).order_by("-updated_at")[:limit]),
            ("potential opportunity", HomepagePotentialOpportunityItem.objects.filter(homepage=content).order_by("-updated_at")[:limit]),
            ("facility", HomepageFacility.objects.filter(homepage=content).order_by("-updated_at")[:limit]),
            ("gallery item", HomepageGalleryItem.objects.filter(homepage=content).order_by("-updated_at")[:limit]),
            ("footer link", HomepageFooterLink.objects.filter(homepage=content).order_by("-updated_at")[:limit]),
            ("stat item", HomepageStatisticItem.objects.filter(homepage=content).order_by("-updated_at")[:limit]),
        ]
        for label, queryset in child_sources:
            for item in queryset:
                title = getattr(item, "title", None) or getattr(item, "label", None) or getattr(item, "alt", None) or label.title()
                items.append(
                    {
                        "module": "homepage",
                        "action": "updated",
                        "title": f"Homepage {label}: {title}",
                        "created_at": item.updated_at,
                        "target_id": str(item.id),
                        "target_url": "/api/v1/homepage/admin/content",
                    }
                )
        items.sort(key=lambda item: item["created_at"], reverse=True)
        return items[:limit]
