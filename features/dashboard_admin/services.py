from __future__ import annotations

from collections import defaultdict
from statistics import mean

from django.core.cache import cache
from django.urls import NoReverseMatch, reverse

from features.dashboard_admin.domain import (
    PENGADUAN_ACTIVE_STATUSES,
    PENGADUAN_DONE_STATUSES,
    SURAT_ACTIVE_STATUSES,
    build_alert,
    calculate_profile_completeness,
    ensure_dashboard_access,
    get_age_hours,
    get_aging_bucket,
    get_scope_start,
    is_attention_needed,
    validate_filters,
)
from features.dashboard_admin.repositories import DashboardRepository
from toolbox.logging import get_logger


class DashboardService:
    def __init__(self, repo: DashboardRepository = None):
        self.repo = repo or DashboardRepository()
        self.logger = get_logger("features.dashboard_admin.services")

    def get_analitik_lengkap(self, actor) -> dict:
        overview = self.get_overview(actor)["data"]
        return {
            "summary": overview["summary"],
            "charts": {
                "surat_by_status": overview["charts"]["surat_by_status"],
                "pengaduan_by_kategori": overview["charts"]["pengaduan_by_kategori"],
            },
        }

    def get_overview(self, actor) -> dict:
        self._ensure_access(actor)
        return self._cached("overview", lambda: {
            "data": {
                "summary": self.repo.get_summary_metrics(),
                "alerts": self._build_alerts(),
                "charts": {
                    "surat_by_status": self.repo.get_surat_stats_by_status(),
                    "pengaduan_by_kategori": self.repo.get_pengaduan_stats_by_kategori(),
                    "surat_trend": self._serialize_trend(self.repo.get_surat_trend()),
                    "pengaduan_trend": self._serialize_trend(self.repo.get_pengaduan_trend()),
                },
                "health": {
                    "content_flags": self._build_content_flags(),
                    "master_flags": self._build_master_flags(),
                },
                "quick_actions": self._build_quick_actions(),
            }
        }, timeout=120)

    def get_surat_queue(self, actor, filters: dict | None = None) -> dict:
        self._ensure_access(actor)
        params = validate_filters(**(filters or {}))

        def loader():
            queryset = self.repo.get_surat_queue_queryset().filter(status__in=SURAT_ACTIVE_STATUSES)
            if params.status:
                queryset = queryset.filter(status=params.status)
            start = get_scope_start(params.scope)
            if start:
                queryset = queryset.filter(created_at__gte=start)

            items = [self._serialize_surat_queue_item(item) for item in queryset.order_by("created_at")]
            if params.aging:
                items = [item for item in items if item["aging_bucket"] == params.aging]
            return {
                "data": items,
                "meta": {
                    "scope": params.scope,
                    "status": params.status,
                    "aging": params.aging,
                    "total": len(items),
                },
            }

        return self._cached(f"surat_queue:{params.scope}:{params.status}:{params.aging}", loader, timeout=60)

    def get_pengaduan_queue(self, actor, filters: dict | None = None) -> dict:
        self._ensure_access(actor)
        params = validate_filters(**(filters or {}))

        def loader():
            queryset = self.repo.get_pengaduan_queue_queryset().filter(status__in=PENGADUAN_ACTIVE_STATUSES)
            if params.status:
                queryset = queryset.filter(status=params.status)
            start = get_scope_start(params.scope)
            if start:
                queryset = queryset.filter(created_at__gte=start)

            items = [self._serialize_pengaduan_queue_item(item) for item in queryset.order_by("created_at")]
            if params.aging:
                items = [item for item in items if item["aging_bucket"] == params.aging]
            return {
                "data": items,
                "meta": {
                    "scope": params.scope,
                    "status": params.status,
                    "aging": params.aging,
                    "total": len(items),
                },
            }

        return self._cached(f"pengaduan_queue:{params.scope}:{params.status}:{params.aging}", loader, timeout=60)

    def get_recent_activity(self, actor, limit: int = 10) -> dict:
        self._ensure_access(actor)

        def loader():
            items = []
            items.extend(self._serialize_surat_activity(item) for item in self.repo.get_surat_histories(limit))
            items.extend(self._serialize_pengaduan_activity(item) for item in self.repo.get_pengaduan_histories(limit))
            items.extend(self._serialize_publikasi_activity(item) for item in self.repo.get_recent_publications(limit))
            items.extend(self._serialize_user_activity(item) for item in self.repo.get_recent_users(limit))
            items.extend(self.repo.get_recent_homepage_activity(limit))
            items.sort(key=lambda item: item["created_at"], reverse=True)
            return {
                "data": items[:limit],
                "meta": {"limit": limit, "returned": min(limit, len(items))},
            }

        return self._cached(f"recent_activity:{limit}", loader, timeout=60)

    def get_surat_analytics(self, actor, period_days: int = 7) -> dict:
        self._ensure_access(actor)

        def loader():
            completed = self.repo.get_surat_completion_candidates()
            durations = [
                round((item.done_at - item.created_at).total_seconds() / 3600, 2)
                for item in completed
                if getattr(item, "done_at", None)
            ]
            missing_documents = self.repo.get_surat_missing_documents()
            return {
                "data": {
                    "by_status": self.repo.get_surat_stats_by_status(),
                    "by_jenis": self.repo.get_surat_stats_by_jenis(),
                    "trend": self._serialize_trend(self.repo.get_surat_trend(period_days)),
                    "summary": {
                        "average_completion_hours": round(mean(durations), 2) if durations else 0,
                        "total_completed": len(durations),
                        "missing_document_total": len(missing_documents),
                    },
                    "top_rejection_reasons": self.repo.get_surat_rejection_stats()[:5],
                    "missing_documents": [self._serialize_surat_queue_item(item) for item in missing_documents[:10]],
                }
            }

        return self._cached(f"surat_analytics:{period_days}", loader, timeout=180)

    def get_pengaduan_analytics(self, actor, period_days: int = 7) -> dict:
        self._ensure_access(actor)

        def loader():
            candidates = self.repo.get_pengaduan_response_candidates()
            response_hours = []
            resolved_hours = []
            for item in candidates:
                if getattr(item, "first_response_at", None):
                    response_hours.append(round((item.first_response_at - item.created_at).total_seconds() / 3600, 2))
                if getattr(item, "resolved_at", None):
                    resolved_hours.append(round((item.resolved_at - item.created_at).total_seconds() / 3600, 2))

            oldest_active = self.repo.get_oldest_active_pengaduan()
            return {
                "data": {
                    "by_status": self.repo.get_pengaduan_stats_by_status(),
                    "by_kategori": self.repo.get_pengaduan_stats_by_kategori(),
                    "trend": self._serialize_trend(self.repo.get_pengaduan_trend(period_days)),
                    "summary": {
                        "average_first_response_hours": round(mean(response_hours), 2) if response_hours else 0,
                        "average_resolved_hours": round(mean(resolved_hours), 2) if resolved_hours else 0,
                        "oldest_active_total": len(oldest_active),
                    },
                    "oldest_active": [self._serialize_pengaduan_queue_item(item) for item in oldest_active],
                    "top_categories": self.repo.get_pengaduan_stats_by_kategori()[:5],
                }
            }

        return self._cached(f"pengaduan_analytics:{period_days}", loader, timeout=180)

    def get_content_health(self, actor) -> dict:
        self._ensure_access(actor)
        return self._cached("content_health", lambda: {
            "data": {
                "flags": self._build_content_flags(),
                "summary": self._build_content_health_summary(),
            }
        }, timeout=180)

    def get_master_health(self, actor) -> dict:
        self._ensure_access(actor)
        return self._cached("master_health", lambda: {
            "data": {
                "flags": self._build_master_flags(),
                "summary": self._build_master_health_summary(),
            }
        }, timeout=180)

    def _ensure_access(self, actor) -> None:
        ensure_dashboard_access(actor)

    def _cached(self, key: str, loader, timeout: int):
        cache_key = f"dashboard_admin:{key}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        data = loader()
        cache.set(cache_key, data, timeout)
        return data

    def _build_alerts(self) -> list[dict]:
        surat_warning = len(self.get_surat_queue_stub(aging="warning"))
        surat_overdue = len(self.get_surat_queue_stub(aging="overdue"))
        pengaduan_warning = len(self.get_pengaduan_queue_stub(aging="warning"))
        pengaduan_overdue = len(self.get_pengaduan_queue_stub(aging="overdue"))
        homepage_status = self.repo.get_homepage_section_status()

        alerts = []
        if surat_overdue:
            alerts.append(build_alert("Surat melewati SLA perlu diproses segera.", "critical", surat_overdue, "surat-overdue"))
        if pengaduan_overdue:
            alerts.append(build_alert("Pengaduan aktif melewati SLA.", "critical", pengaduan_overdue, "pengaduan-overdue"))
        if homepage_status["important_missing"]:
            alerts.append(
                build_alert(
                    "Section penting homepage masih kosong.",
                    "warning",
                    len(homepage_status["important_missing"]),
                    "homepage-missing-important",
                )
            )
        if surat_warning:
            alerts.append(build_alert("Ada surat mendekati SLA.", "warning", surat_warning, "surat-warning"))
        if pengaduan_warning:
            alerts.append(build_alert("Ada pengaduan mendekati SLA.", "warning", pengaduan_warning, "pengaduan-warning"))
        if not alerts:
            alerts.append(build_alert("Tidak ada antrean kritis saat ini.", "info", 0, "all-good"))
        return alerts

    def get_surat_queue_stub(self, aging: str) -> list[dict]:
        queryset = self.repo.get_surat_queue_queryset().filter(status__in=SURAT_ACTIVE_STATUSES).order_by("created_at")
        items = [self._serialize_surat_queue_item(item) for item in queryset]
        return [item for item in items if item["aging_bucket"] == aging]

    def get_pengaduan_queue_stub(self, aging: str) -> list[dict]:
        queryset = self.repo.get_pengaduan_queue_queryset().filter(status__in=PENGADUAN_ACTIVE_STATUSES).order_by("created_at")
        items = [self._serialize_pengaduan_queue_item(item) for item in queryset]
        return [item for item in items if item["aging_bucket"] == aging]

    def _build_quick_actions(self) -> list[dict]:
        summary = self.repo.get_summary_metrics()
        homepage_status = self.repo.get_homepage_section_status()
        return [
            self._quick_action("surat-pending", "Lihat surat pending", "surat-list", "/admin/surat?status=PENDING", summary["surat_pending"], "surat"),
            self._quick_action("pengaduan-aktif", "Lihat pengaduan aktif", "pengaduan-list", "/admin/pengaduan?status=OPEN", summary["pengaduan_aktif"], "pengaduan"),
            self._quick_action("buat-publikasi", "Buat publikasi", "publikasi-admin-buat", "/admin/publikasi/buat", 0, "publikasi"),
            self._quick_action("kelola-homepage", "Kelola homepage", "homepage-admin-content", "/admin/homepage", homepage_status["empty_sections"], "homepage"),
            self._quick_action("tambah-dusun", "Tambah dusun", "dashboard-overview", "/admin/profil-wilayah/dusun/buat", 0, "profil"),
            self._quick_action("tambah-perangkat", "Tambah perangkat desa", "dashboard-overview", "/admin/profil-wilayah/perangkat/buat", 0, "profil"),
            self._quick_action("kelola-usaha", "Kelola unit usaha", "ekonomi-admin-list", "/admin/potensi-ekonomi", summary["total_unit_published"], "ekonomi"),
        ]

    def _quick_action(self, key: str, label: str, route_name: str, fallback_path: str, badge_count: int, category: str) -> dict:
        return {
            "key": key,
            "label": label,
            "route_name": route_name,
            "path": self._reverse_or_fallback(route_name, fallback_path),
            "badge_count": badge_count,
            "category": category,
        }

    def _build_content_flags(self) -> list[dict]:
        draft_publications = self.repo.get_draft_publications()
        unpublished_units = self.repo.get_unpublished_units()
        unpublished_perangkat = self.repo.get_unpublished_perangkat()
        homepage_status = self.repo.get_homepage_section_status()

        flags = [
            {
                "key": "publikasi-draft",
                "label": "Publikasi draft",
                "total": len(draft_publications),
                "severity": "warning" if draft_publications else "info",
                "detail": f"Draft terlama: {draft_publications[0].judul}" if draft_publications else None,
            },
            {
                "key": "unit-unpublished",
                "label": "Unit ekonomi belum tayang",
                "total": len(unpublished_units),
                "severity": "warning" if unpublished_units else "info",
                "detail": unpublished_units[0].nama_usaha if unpublished_units else None,
            },
            {
                "key": "perangkat-unpublished",
                "label": "Perangkat belum tayang",
                "total": len(unpublished_perangkat),
                "severity": "warning" if unpublished_perangkat else "info",
                "detail": unpublished_perangkat[0].user.nama_lengkap if unpublished_perangkat else None,
            },
            {
                "key": "homepage-content",
                "label": "Konten homepage belum lengkap",
                "total": homepage_status["empty_sections"],
                "severity": "warning" if homepage_status["empty_sections"] else "info",
                "detail": f"Terisi {homepage_status['filled_sections']}/{homepage_status['total_sections']} section ({homepage_status['completeness_score']}%)",
            },
            {
                "key": "homepage-important-missing",
                "label": "Section penting homepage kosong",
                "total": len(homepage_status["important_missing"]),
                "severity": "critical" if homepage_status["important_missing"] else "info",
                "detail": ", ".join(homepage_status["important_missing"][:4]) if homepage_status["important_missing"] else None,
            },
        ]
        return flags

    def _build_master_flags(self) -> list[dict]:
        profile = self.repo.get_profile()
        completeness = calculate_profile_completeness(profile)
        user_status = self.repo.get_user_status_counts()
        unpublished_perangkat = self.repo.get_total_perangkat_count() - self.repo.get_published_perangkat_count()

        return [
            {
                "key": "profil-desa",
                "label": "Kelengkapan profil desa",
                "total": completeness["score"],
                "severity": "info" if completeness["is_complete"] else "warning",
                "detail": f"Visi={completeness['visi']}, Misi={completeness['misi']}, Sejarah={completeness['sejarah']}",
            },
            {
                "key": "akun-inactive",
                "label": "Akun nonaktif",
                "total": user_status["inactive"],
                "severity": "warning" if user_status["inactive"] else "info",
                "detail": None,
            },
            {
                "key": "perangkat-hidden",
                "label": "Perangkat belum published",
                "total": unpublished_perangkat,
                "severity": "warning" if unpublished_perangkat else "info",
                "detail": None,
            },
        ]

    def _build_content_health_summary(self) -> dict:
        drafts = self.repo.get_draft_publications()
        published = self.repo.get_published_publications_count()
        unpublished_units = self.repo.get_unpublished_units()
        unpublished_perangkat = self.repo.get_unpublished_perangkat()
        homepage_status = self.repo.get_homepage_section_status()
        return {
            "draft_publications": len(drafts),
            "published_publications": published,
            "oldest_draft_title": drafts[0].judul if drafts else None,
            "unpublished_units": len(unpublished_units),
            "unpublished_perangkat": len(unpublished_perangkat),
            "homepage_filled_sections": homepage_status["filled_sections"],
            "homepage_empty_sections": homepage_status["empty_sections"],
            "homepage_total_sections": homepage_status["total_sections"],
            "homepage_completeness_score": homepage_status["completeness_score"],
            "homepage_important_missing": homepage_status["important_missing"],
            "homepage_list_counts": homepage_status["list_counts"],
        }

    def _build_master_health_summary(self) -> dict:
        profile = self.repo.get_profile()
        completeness = calculate_profile_completeness(profile)
        role_counts = self.repo.get_user_role_counts()
        user_status = self.repo.get_user_status_counts()
        return {
            "dusun_total": self.repo.get_total_dusun_count(),
            "perangkat_published": self.repo.get_published_perangkat_count(),
            "perangkat_total": self.repo.get_total_perangkat_count(),
            "profile_completeness": completeness,
            "user_status": user_status,
            "role_counts": role_counts,
        }

    def _serialize_surat_queue_item(self, surat) -> dict:
        return {
            "id": str(surat.id),
            "module": "surat",
            "title": f"{surat.jenis_surat} - {surat.keperluan[:40]}",
            "subject_name": surat.pemohon.nama_lengkap,
            "status": surat.status,
            "created_at": surat.created_at,
            "updated_at": surat.updated_at,
            "age_hours": get_age_hours(surat.created_at),
            "aging_bucket": get_aging_bucket(surat.created_at),
            "attention_needed": is_attention_needed(surat.created_at),
            "detail_url": self._reverse_or_fallback("surat-detail", f"/api/v1/layanan-administrasi/mvp/surat/{surat.id}"),
        }

    def _serialize_pengaduan_queue_item(self, pengaduan) -> dict:
        return {
            "id": str(pengaduan.id),
            "module": "pengaduan",
            "title": pengaduan.judul,
            "subject_name": pengaduan.pelapor.nama_lengkap,
            "status": pengaduan.status,
            "created_at": pengaduan.created_at,
            "updated_at": pengaduan.updated_at,
            "age_hours": get_age_hours(pengaduan.created_at),
            "aging_bucket": get_aging_bucket(pengaduan.created_at),
            "attention_needed": is_attention_needed(pengaduan.created_at),
            "detail_url": self._reverse_or_fallback("pengaduan-detail", f"/api/v1/pengaduan/mvp/{pengaduan.id}"),
        }

    def _serialize_surat_activity(self, history) -> dict:
        return {
            "module": "surat",
            "action": history.status_to.lower(),
            "title": f"Surat {history.surat.jenis_surat} -> {history.status_to}",
            "actor_name": getattr(history.changed_by, "nama_lengkap", None),
            "created_at": history.created_at,
            "target_id": str(history.surat.id),
            "target_url": self._reverse_or_fallback("surat-detail", f"/api/v1/layanan-administrasi/mvp/surat/{history.surat.id}"),
        }

    def _serialize_pengaduan_activity(self, history) -> dict:
        return {
            "module": "pengaduan",
            "action": history.status_to.lower(),
            "title": f"Pengaduan {history.pengaduan.judul} -> {history.status_to}",
            "actor_name": getattr(history.changed_by, "nama_lengkap", None),
            "created_at": history.created_at,
            "target_id": str(history.pengaduan.id),
            "target_url": self._reverse_or_fallback("pengaduan-detail", f"/api/v1/pengaduan/mvp/{history.pengaduan.id}"),
        }

    def _serialize_publikasi_activity(self, publikasi) -> dict:
        action = "published" if publikasi.status == "PUBLISHED" else "updated"
        timestamp = publikasi.published_at or publikasi.updated_at or publikasi.created_at
        return {
            "module": "publikasi",
            "action": action,
            "title": publikasi.judul,
            "actor_name": getattr(publikasi.penulis, "nama_lengkap", None),
            "created_at": timestamp,
            "target_id": str(publikasi.id),
            "target_url": self._reverse_or_fallback("publikasi-detail", f"/api/v1/publikasi/mvp/publik/{publikasi.slug}"),
        }

    def _serialize_user_activity(self, user) -> dict:
        action = "activated" if user.is_active and user.created_at != user.updated_at else "created"
        if not user.is_active:
            action = "deactivated"
        return {
            "module": "auth",
            "action": action,
            "title": f"Akun {user.nama_lengkap}",
            "actor_name": None,
            "created_at": user.updated_at or user.created_at,
            "target_id": str(user.id),
            "target_url": "/admin/auth/user-management",
        }

    def _serialize_trend(self, points: list[dict]) -> list[dict]:
        grouped = defaultdict(int)
        for point in points:
            grouped[str(point["day"])] += point["total"]
        return [{"date": day, "total": total} for day, total in sorted(grouped.items(), key=lambda item: item[0])]

    def _reverse_or_fallback(self, route_name: str, fallback: str) -> str:
        try:
            return reverse(route_name)
        except NoReverseMatch:
            return fallback
