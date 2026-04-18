from features.profil_wilayah.models import WilayahDusun, WilayahPerangkat, ProfilDesa


class DusunRepository:
    def list_all(self):
        return WilayahDusun.objects.all().order_by("id")

    def get_by_id(self, dusun_id: int) -> WilayahDusun:
        return WilayahDusun.objects.get(id=dusun_id)

    def create(self, nama_dusun: str, kepala_dusun: str) -> WilayahDusun:
        return WilayahDusun.objects.create(
            nama_dusun=nama_dusun,
            kepala_dusun=kepala_dusun,
        )

    def update(self, dusun_id: int, nama_dusun: str, kepala_dusun: str) -> WilayahDusun:
        dusun = self.get_by_id(dusun_id)
        dusun.nama_dusun = nama_dusun
        dusun.kepala_dusun = kepala_dusun
        dusun.save()
        return dusun

    def delete(self, dusun_id: int) -> None:
        dusun = self.get_by_id(dusun_id)
        dusun.delete()


class PerangkatRepository:
    def list_published(self):
        return (
            WilayahPerangkat.objects
            .select_related("user")
            .filter(is_published=True)
            .order_by("id")
        )

    def list_all(self):
        return (
            WilayahPerangkat.objects
            .select_related("user")
            .all()
            .order_by("id")
        )

    def get_by_id(self, perangkat_id: int) -> WilayahPerangkat:
        return WilayahPerangkat.objects.select_related("user").get(id=perangkat_id)

    def create(self, user_id, jabatan: str, is_published: bool, foto=None) -> WilayahPerangkat:
        return WilayahPerangkat.objects.create(
            user_id=user_id,
            jabatan=jabatan,
            is_published=is_published,
            foto=foto,
        )

    def update(
        self,
        perangkat_id: int,
        user_id,
        jabatan: str,
        is_published: bool,
        foto=None,
    ) -> WilayahPerangkat:
        perangkat = self.get_by_id(perangkat_id)
        perangkat.user_id = user_id
        perangkat.jabatan = jabatan
        perangkat.is_published = is_published

        if foto is not None:
            perangkat.foto = foto

        perangkat.save()
        return perangkat

    def delete(self, perangkat_id: int) -> None:
        perangkat = self.get_by_id(perangkat_id)
        perangkat.delete()


class ProfilDesaRepository:
    def get_profil(self) -> ProfilDesa:
        profil, _ = ProfilDesa.objects.get_or_create(
            id=1,
            defaults={
                "visi": "Visi Desa",
                "misi": "Misi Desa",
                "sejarah": "Sejarah Desa",
            },
        )
        return profil

    def update_profil(self, visi: str, misi: str, sejarah: str) -> ProfilDesa:
        profil = self.get_profil()
        profil.visi = visi
        profil.misi = misi
        profil.sejarah = sejarah
        profil.save()
        return profil