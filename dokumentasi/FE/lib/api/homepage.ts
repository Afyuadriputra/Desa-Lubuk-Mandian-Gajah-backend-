import { ekonomiApi } from "@/lib/api/ekonomi";
import { profilApi } from "@/lib/api/profil";
import { publikasiApi } from "@/lib/api/publikasi";

export async function getHomepageBackendData() {
  const [profil, publikasi, ekonomi] = await Promise.all([
    profilApi.getPublik(),
    publikasiApi.listPublik(),
    ekonomiApi.listPublik(),
  ]);

  return {
    profil,
    publikasi,
    ekonomi,
  };
}
