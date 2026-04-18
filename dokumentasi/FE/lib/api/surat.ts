import { apiRequest } from "@/lib/api/client";
import type { ApiEnvelope, SuratDetailDto, SuratDto } from "@/lib/api/types";

type AjukanSuratPayload = {
  jenis_surat: "SKU" | "SKTM" | "DOMISILI";
  keperluan: string;
};

type ProsesSuratPayload = {
  status: "VERIFIED" | "PROCESSED" | "DONE" | "REJECTED";
  notes?: string | null;
  nomor_surat?: string | null;
  rejection_reason?: string | null;
};

export const suratApi = {
  ajukan: (payload: AjukanSuratPayload) =>
    apiRequest<ApiEnvelope<SuratDto>>("/layanan-administrasi/mvp/surat/ajukan", {
      method: "POST",
      body: payload,
    }),

  list: () =>
    apiRequest<ApiEnvelope<SuratDto[]>>("/layanan-administrasi/mvp/surat"),

  detail: (suratId: string) =>
    apiRequest<ApiEnvelope<SuratDetailDto>>(`/layanan-administrasi/mvp/surat/${suratId}`),

  proses: (suratId: string, payload: ProsesSuratPayload) =>
    apiRequest<ApiEnvelope<SuratDto>>(`/layanan-administrasi/mvp/surat/${suratId}/proses`, {
      method: "POST",
      body: payload,
    }),

  getDownloadUrl: (suratId: string) =>
    `/api/v1/layanan-administrasi/mvp/surat/${suratId}/download`,
};
