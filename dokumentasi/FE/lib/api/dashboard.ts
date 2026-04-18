import { apiRequest } from "@/lib/api/client";
import type {
  DashboardActivityDto,
  DashboardAnalyticsDto,
  DashboardHealthDto,
  DashboardOverviewDto,
  DashboardQueueDto,
} from "@/lib/api/types";

type QueueFilters = {
  scope?: "today" | "week" | "all";
  status?: string;
  aging?: "warning" | "overdue";
};

function withQuery(path: string, params: Record<string, string | number | undefined>) {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") {
      query.set(key, String(value));
    }
  }
  const queryString = query.toString();
  return queryString ? `${path}?${queryString}` : path;
}

export const dashboardApi = {
  overview: () => apiRequest<{ data: DashboardOverviewDto }>("/dashboard-admin/overview"),

  suratQueue: (filters: QueueFilters = {}) =>
    apiRequest<DashboardQueueDto>(
      withQuery("/dashboard-admin/surat-queue", filters),
    ),

  pengaduanQueue: (filters: QueueFilters = {}) =>
    apiRequest<DashboardQueueDto>(
      withQuery("/dashboard-admin/pengaduan-queue", filters),
    ),

  recentActivity: (limit = 10) =>
    apiRequest<DashboardActivityDto>(
      withQuery("/dashboard-admin/recent-activity", { limit }),
    ),

  suratAnalytics: (periodDays = 7) =>
    apiRequest<DashboardAnalyticsDto>(
      withQuery("/dashboard-admin/surat-analytics", { period_days: periodDays }),
    ),

  pengaduanAnalytics: (periodDays = 7) =>
    apiRequest<DashboardAnalyticsDto>(
      withQuery("/dashboard-admin/pengaduan-analytics", { period_days: periodDays }),
    ),

  contentHealth: () =>
    apiRequest<DashboardHealthDto>("/dashboard-admin/content-health"),

  masterHealth: () =>
    apiRequest<DashboardHealthDto>("/dashboard-admin/master-health"),
};
