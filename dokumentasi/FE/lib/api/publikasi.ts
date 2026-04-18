import { apiRequest } from "@/lib/api/client";
import type { ApiEnvelope, PublikasiDetailDto, PublikasiListItemDto } from "@/lib/api/types";

type PublikasiPayload = {
  judul: string;
  konten_html: string;
  jenis: "BERITA" | "PENGUMUMAN";
  status?: "DRAFT" | "PUBLISHED";
};

type PublikasiStatusPayload = {
  status: "DRAFT" | "PUBLISHED";
};

export const publikasiApi = {
  listPublik: () =>
    apiRequest<ApiEnvelope<PublikasiListItemDto[]>>("/publikasi/mvp/publik"),

  detailPublik: (slug: string) =>
    apiRequest<ApiEnvelope<PublikasiDetailDto>>(`/publikasi/mvp/publik/${slug}`),

  create: (payload: PublikasiPayload) =>
    apiRequest<PublikasiDetailDto>("/publikasi/admin/buat", {
      method: "POST",
      body: payload,
    }),

  update: (slug: string, payload: PublikasiPayload) =>
    apiRequest<PublikasiDetailDto>(`/publikasi/admin/${slug}`, {
      method: "PUT",
      body: payload,
    }),

  updateStatus: (slug: string, payload: PublikasiStatusPayload) =>
    apiRequest<PublikasiDetailDto>(`/publikasi/admin/${slug}/status`, {
      method: "PUT",
      body: payload,
    }),

  remove: (slug: string) =>
    apiRequest<{ detail: string }>(`/publikasi/admin/${slug}`, {
      method: "DELETE",
    }),
};
