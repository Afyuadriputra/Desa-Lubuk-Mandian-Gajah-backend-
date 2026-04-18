import { apiRequest } from "@/lib/api/client";
import type { ApiEnvelope, PengaduanDetailDto, PengaduanDto } from "@/lib/api/types";

type BuatPengaduanPayload = FormData;

type ProsesPengaduanPayload = {
  status: "TRIAGED" | "IN_PROGRESS" | "RESOLVED" | "CLOSED";
  notes?: string | null;
};

export const pengaduanApi = {
  buat: (payload: BuatPengaduanPayload) =>
    apiRequest<ApiEnvelope<PengaduanDto>>("/pengaduan/mvp/buat", {
      method: "POST",
      body: payload,
    }),

  list: () => apiRequest<ApiEnvelope<PengaduanDto[]>>("/pengaduan/mvp"),

  detail: (pengaduanId: number) =>
    apiRequest<ApiEnvelope<PengaduanDetailDto>>(`/pengaduan/mvp/${pengaduanId}`),

  proses: (pengaduanId: number, payload: ProsesPengaduanPayload) =>
    apiRequest<ApiEnvelope<PengaduanDto>>(`/pengaduan/mvp/${pengaduanId}/proses`, {
      method: "POST",
      body: payload,
    }),
};
