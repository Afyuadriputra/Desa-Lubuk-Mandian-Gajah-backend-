from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from django.utils import timezone

STATUS_SCOPE_TODAY = "today"
STATUS_SCOPE_WEEK = "week"
STATUS_SCOPE_ALL = "all"
VALID_SCOPES = {STATUS_SCOPE_TODAY, STATUS_SCOPE_WEEK, STATUS_SCOPE_ALL}

AGING_WARNING = "warning"
AGING_OVERDUE = "overdue"
VALID_AGING_FILTERS = {AGING_WARNING, AGING_OVERDUE}

SURAT_ACTIVE_STATUSES = {"PENDING", "VERIFIED", "PROCESSED"}
PENGADUAN_ACTIVE_STATUSES = {"OPEN", "TRIAGED", "IN_PROGRESS"}
PENGADUAN_DONE_STATUSES = {"RESOLVED", "CLOSED"}

SLA_WARNING_HOURS = 24
SLA_OVERDUE_HOURS = 72


class DashboardError(Exception):
    """Base exception untuk modul dashboard."""


class DashboardAccessError(DashboardError):
    """Akses ditolak untuk melihat analitik dashboard."""


class DashboardValidationError(DashboardError):
    """Input filter dashboard tidak valid."""


@dataclass(frozen=True)
class DashboardFilters:
    scope: str = STATUS_SCOPE_ALL
    status: str | None = None
    aging: str | None = None


def ensure_dashboard_access(actor) -> None:
    if not actor or not getattr(actor, "is_authenticated", False):
        raise DashboardAccessError("Unauthorized.")
    if not getattr(actor, "is_active", False) or not getattr(actor, "is_staff", False):
        raise DashboardAccessError("Anda tidak memiliki hak akses ke Dashboard Admin.")


def validate_filters(scope: str = STATUS_SCOPE_ALL, status: str | None = None, aging: str | None = None) -> DashboardFilters:
    normalized_scope = (scope or STATUS_SCOPE_ALL).lower()
    if normalized_scope not in VALID_SCOPES:
        raise DashboardValidationError(f"Scope '{scope}' tidak valid.")

    normalized_aging = aging.lower() if aging else None
    if normalized_aging and normalized_aging not in VALID_AGING_FILTERS:
        raise DashboardValidationError(f"Filter aging '{aging}' tidak valid.")

    return DashboardFilters(scope=normalized_scope, status=status, aging=normalized_aging)


def get_scope_start(scope: str):
    now = timezone.now()
    if scope == STATUS_SCOPE_TODAY:
        return now - timedelta(days=1)
    if scope == STATUS_SCOPE_WEEK:
        return now - timedelta(days=7)
    return None


def get_age_hours(created_at):
    if not created_at:
        return 0
    delta = timezone.now() - created_at
    return max(0, int(delta.total_seconds() // 3600))


def get_aging_bucket(created_at) -> str:
    age_hours = get_age_hours(created_at)
    if age_hours >= SLA_OVERDUE_HOURS:
        return AGING_OVERDUE
    if age_hours >= SLA_WARNING_HOURS:
        return AGING_WARNING
    return "normal"


def is_attention_needed(created_at) -> bool:
    return get_aging_bucket(created_at) in {AGING_WARNING, AGING_OVERDUE}


def build_alert(message: str, severity: str, metric: int, key: str) -> dict:
    return {
        "key": key,
        "message": message,
        "severity": severity,
        "metric": metric,
    }


def calculate_profile_completeness(profil_desa) -> dict:
    visi_ready = bool(getattr(profil_desa, "visi", "").strip()) if profil_desa else False
    misi_ready = bool(getattr(profil_desa, "misi", "").strip()) if profil_desa else False
    sejarah_ready = bool(getattr(profil_desa, "sejarah", "").strip()) if profil_desa else False
    completed = sum([visi_ready, misi_ready, sejarah_ready])
    total = 3
    return {
        "visi": visi_ready,
        "misi": misi_ready,
        "sejarah": sejarah_ready,
        "score": int((completed / total) * 100),
        "is_complete": completed == total,
    }
