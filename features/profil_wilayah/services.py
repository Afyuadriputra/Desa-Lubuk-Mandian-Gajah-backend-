# features/profil_wilayah/services.py

from features.profil_wilayah.domain import (
    validate_dusun,
    validate_perangkat,
    validate_profil_desa,
)
from features.profil_wilayah.permissions import can_manage_data_wilayah
from features.profil_wilayah.repositories import (
    DusunRepository,
    PerangkatRepository,
    ProfilDesaRepository,
)
from toolbox.logging import audit_event
from toolbox.security.upload_validators import validate_image_upload


class ProfilWilayahAccessError(Exception):
    pass


class DusunService:
    def __init__(self, repo: DusunRepository = None):
        self.repo = repo or DusunRepository()

    def tambah_dusun(self, actor, nama_dusun: str, kepala_dusun: str):
        self._ensure_can_manage(actor)
        validate_dusun(nama_dusun, kepala_dusun)

        dusun = self.repo.create(nama_dusun, kepala_dusun)
        audit_event("DUSUN_CREATED", actor_id=actor.id, target_id=dusun.id)
        return dusun

    def ubah_dusun(self, actor, dusun_id: int, nama_dusun: str, kepala_dusun: str):
        self._ensure_can_manage(actor)
        validate_dusun(nama_dusun, kepala_dusun)

        dusun = self.repo.update(dusun_id, nama_dusun, kepala_dusun)
        audit_event("DUSUN_UPDATED", actor_id=actor.id, target_id=dusun.id)
        return dusun

    def hapus_dusun(self, actor, dusun_id: int):
        self._ensure_can_manage(actor)
        self.repo.delete(dusun_id)
        audit_event("DUSUN_DELETED", actor_id=actor.id, target_id=dusun_id)

    def get_semua_dusun(self):
        return self.repo.list_all()

    def _ensure_can_manage(self, actor):
        if not can_manage_data_wilayah(actor):
            raise ProfilWilayahAccessError("Akses ditolak.")


class PerangkatService:
    def __init__(self, repo: PerangkatRepository = None):
        self.repo = repo or PerangkatRepository()

    def tambah_perangkat(self, actor, user_id, jabatan: str, is_published: bool, foto=None):
        self._ensure_can_manage(actor)
        validate_perangkat(jabatan)
        self._validate_foto_if_present(foto)

        perangkat = self.repo.create(user_id, jabatan, is_published, foto)
        audit_event("PERANGKAT_CREATED", actor_id=actor.id, target_id=perangkat.id)
        return perangkat

    def ubah_perangkat(
        self,
        actor,
        perangkat_id: int,
        user_id,
        jabatan: str,
        is_published: bool,
        foto=None,
    ):
        self._ensure_can_manage(actor)
        validate_perangkat(jabatan)
        self._validate_foto_if_present(foto)

        perangkat = self.repo.update(
            perangkat_id=perangkat_id,
            user_id=user_id,
            jabatan=jabatan,
            is_published=is_published,
            foto=foto,
        )
        audit_event("PERANGKAT_UPDATED", actor_id=actor.id, target_id=perangkat.id)
        return perangkat

    def hapus_perangkat(self, actor, perangkat_id: int):
        self._ensure_can_manage(actor)
        self.repo.delete(perangkat_id)
        audit_event("PERANGKAT_DELETED", actor_id=actor.id, target_id=perangkat_id)

    def get_perangkat_publik(self):
        return self.repo.list_published()

    def get_semua_perangkat(self):
        return self.repo.list_all()

    def _ensure_can_manage(self, actor):
        if not can_manage_data_wilayah(actor):
            raise ProfilWilayahAccessError("Akses ditolak.")

    def _validate_foto_if_present(self, foto):
        if foto:
            validate_image_upload(foto)


class ProfilDesaService:
    def __init__(self, repo: ProfilDesaRepository = None):
        self.repo = repo or ProfilDesaRepository()

    def perbarui_profil(self, actor, visi: str, misi: str, sejarah: str):
        if not can_manage_data_wilayah(actor):
            raise ProfilWilayahAccessError("Akses ditolak.")

        validate_profil_desa(visi, misi, sejarah)
        profil = self.repo.update_profil(visi, misi, sejarah)
        audit_event("PROFIL_DESA_UPDATED", actor_id=actor.id)
        return profil

    def get_profil(self):
        return self.repo.get_profil()