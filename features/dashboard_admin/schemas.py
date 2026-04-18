from __future__ import annotations

from datetime import datetime
from typing import Any

from ninja import Schema


class OverviewSummarySchema(Schema):
    total_pengajuan_surat_hari_ini: int
    surat_pending: int
    surat_verified: int
    surat_processed: int
    surat_done: int
    surat_rejected: int
    pengaduan_aktif: int
    pengaduan_selesai: int
    total_warga_aktif: int
    total_unit_published: int


class AlertItemSchema(Schema):
    key: str
    message: str
    severity: str
    metric: int


class ChartItemSchema(Schema):
    label: str
    total: int


class TrendPointSchema(Schema):
    date: str
    total: int


class QueueItemSchema(Schema):
    id: str
    module: str
    title: str
    subject_name: str
    status: str
    created_at: datetime
    updated_at: datetime
    age_hours: int
    aging_bucket: str
    attention_needed: bool
    detail_url: str


class QueueMetaSchema(Schema):
    scope: str
    status: str | None = None
    aging: str | None = None
    total: int


class QueueResponseSchema(Schema):
    data: list[QueueItemSchema]
    meta: QueueMetaSchema


class ActivityItemSchema(Schema):
    module: str
    action: str
    title: str
    actor_name: str | None = None
    created_at: datetime
    target_id: str
    target_url: str


class RecentActivityResponseSchema(Schema):
    data: list[ActivityItemSchema]
    meta: dict[str, int]


class HealthFlagSchema(Schema):
    key: str
    label: str
    total: int
    severity: str
    detail: str | None = None


class QuickActionSchema(Schema):
    key: str
    label: str
    route_name: str
    path: str
    badge_count: int = 0
    category: str


class OverviewChartsSchema(Schema):
    surat_by_status: list[ChartItemSchema]
    pengaduan_by_kategori: list[ChartItemSchema]
    surat_trend: list[TrendPointSchema]
    pengaduan_trend: list[TrendPointSchema]


class OverviewHealthSchema(Schema):
    content_flags: list[HealthFlagSchema]
    master_flags: list[HealthFlagSchema]


class DashboardOverviewDataSchema(Schema):
    summary: OverviewSummarySchema
    alerts: list[AlertItemSchema]
    charts: OverviewChartsSchema
    health: OverviewHealthSchema
    quick_actions: list[QuickActionSchema]


class DashboardOverviewResponseSchema(Schema):
    data: DashboardOverviewDataSchema


class AnalyticsBlockSchema(Schema):
    items: list[dict[str, Any]] | None = None
    trends: list[TrendPointSchema] | None = None
    summary: dict[str, Any] | None = None


class DashboardAnalyticsResponseSchema(Schema):
    data: dict[str, Any]


class DashboardHealthResponseSchema(Schema):
    data: dict[str, Any]


class LegacyDashboardResponseSchema(Schema):
    data: dict[str, Any]
