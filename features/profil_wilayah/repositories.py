# features/profil_wilayah/repositories.py

from features.profil_wilayah.models import WilayahDusun, WilayahPerangkat, ProfilDesa

class DusunRepository:
    def list_all(self):
        return WilayahDusun.objects.all()

    def create(self, nama_dusun: str, kepala_dusun: str) -> WilayahDusun:
        return WilayahDusun.objects.create(nama_dusun=nama_dusun, kepala_dusun=kepala_dusun)


class PerangkatRepository:
    def list_published(self):
        return WilayahPerangkat.objects.select_related("user").filter(is_published=True)

    def list_all(self):
        return WilayahPerangkat.objects.select_related("user").all()

    def create(self, user_id, jabatan: str, is_published: bool, foto=None) -> WilayahPerangkat:
        return WilayahPerangkat.objects.create(
            user_id=user_id, jabatan=jabatan, is_published=is_published, foto=foto
        )


class ProfilDesaRepository:
    def get_profil(self) -> ProfilDesa:
        profil, _ = ProfilDesa.objects.get_or_create(id=1, defaults={
            "visi": "Visi Desa", "misi": "Misi Desa", "sejarah": "Sejarah Desa"
        })
        return profil

    def update_profil(self, visi: str, misi: str, sejarah: str) -> ProfilDesa:
        profil = self.get_profil()
        profil.visi = visi
        profil.misi = misi
        profil.sejarah = sejarah
        profil.save()
        return profil