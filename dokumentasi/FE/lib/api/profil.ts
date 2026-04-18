import { apiRequest } from "@/lib/api/client";
import type { DusunDto, ProfilDesaDto, ProfilPublikDto } from "@/lib/api/types";

type UpsertDusunPayload = {
  nama_dusun: string;
  kepala_dusun: string;
};

type UpdateProfilPayload = ProfilDesaDto;

export const profilApi = {
  getPublik: () => apiRequest<ProfilPublikDto>("/profil-wilayah/publik"),

  listDusunAdmin: () => apiRequest<DusunDto[]>("/profil-wilayah/admin/dusun"),

  createDusun: (payload: UpsertDusunPayload) =>
    apiRequest<DusunDto>("/profil-wilayah/admin/dusun", { method: "POST", body: payload }),

  updateDusun: (dusunId: number, payload: UpsertDusunPayload) =>
    apiRequest<DusunDto>(`/profil-wilayah/admin/dusun/${dusunId}`, {
      method: "PUT",
      body: payload,
    }),

  deleteDusun: (dusunId: number) =>
    apiRequest<{ detail: string }>(`/profil-wilayah/admin/dusun/${dusunId}`, {
      method: "DELETE",
    }),

  updateProfilDesa: (payload: UpdateProfilPayload) =>
    apiRequest<ProfilDesaDto>("/profil-wilayah/admin/profil", {
      method: "PUT",
      body: payload,
    }),
};
