import { apiRequest } from "@/lib/api/client";
import type { ApiEnvelope, UnitUsahaDetailDto, UnitUsahaListItemDto } from "@/lib/api/types";

type UnitUsahaPayload = {
  nama_usaha: string;
  kategori: "KOPERASI" | "WISATA" | "JASA";
  deskripsi: string;
  fasilitas?: string | null;
  kontak_wa?: string | null;
  harga_tiket?: string | number | null;
  is_published?: boolean;
};

export const ekonomiApi = {
  listPublik: () =>
    apiRequest<ApiEnvelope<UnitUsahaListItemDto[]>>("/potensi-ekonomi/mvp/katalog"),

  detailPublik: (unitId: number) =>
    apiRequest<ApiEnvelope<UnitUsahaDetailDto>>(`/potensi-ekonomi/mvp/${unitId}`),

  listAdmin: () =>
    apiRequest<ApiEnvelope<UnitUsahaListItemDto[]>>("/potensi-ekonomi/mvp/admin/list"),

  create: (payload: UnitUsahaPayload) =>
    apiRequest<ApiEnvelope<UnitUsahaDetailDto>>("/potensi-ekonomi/mvp/admin/buat", {
      method: "POST",
      body: payload,
    }),

  update: (unitId: number, payload: UnitUsahaPayload) =>
    apiRequest<ApiEnvelope<UnitUsahaDetailDto>>(`/potensi-ekonomi/mvp/admin/${unitId}`, {
      method: "PUT",
      body: payload,
    }),

  remove: (unitId: number) =>
    apiRequest<ApiEnvelope<{ detail: string }>>(`/potensi-ekonomi/mvp/admin/${unitId}`, {
      method: "DELETE",
    }),
};
