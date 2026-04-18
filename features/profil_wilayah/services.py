# features/profil_wilayah/services.py

from django.core.exceptions import ValidationError
from features.profil_wilayah.domain import validate_dusun, validate_perangkat, validate_profil_desa
from features.profil_wilayah.permissions import can_manage_data_wilayah
from features.profil_wilayah.repositories import DusunRepository, PerangkatRepository, ProfilDesaRepository
from toolbox.logging import audit_event
from toolbox.security.upload_validators import validate_image_upload

class ProfilWilayahAccessError(Exception):
    pass

class DusunService:
    def __init__(self, repo: DusunRepository = None):
        self.repo = repo or DusunRepository()

    def tambah_dusun(self, actor, nama_dusun: str, kepala_dusun: str):
        if not can_manage_data_wilayah(actor):
            raise ProfilWilayahAccessError("Akses ditolak.")
        validate_dusun(nama_dusun, kepala_dusun)
        dusun = self.repo.create(nama_dusun, kepala_dusun)
        audit_event("DUSUN_CREATED", actor_id=actor.id, target_id=dusun.id)
        return dusun

    def get_semua_dusun(self):
        return self.repo.list_all()


class PerangkatService:
    def __init__(self, repo: PerangkatRepository = None):
        self.repo = repo or PerangkatRepository()

    def tambah_perangkat(self, actor, user_id, jabatan: str, is_published: bool, foto=None):
        if not can_manage_data_wilayah(actor):
            raise ProfilWilayahAccessError("Akses ditolak.")
        validate_perangkat(jabatan)
        
        if foto:
            validate_image_upload(foto)

        perangkat = self.repo.create(user_id, jabatan, is_published, foto)
        audit_event("PERANGKAT_CREATED", actor_id=actor.id, target_id=perangkat.id)
        return perangkat

    def get_perangkat_publik(self):
        return self.repo.list_published()


class ProfilDesaService:
    def __init__(self, repo: ProfilDesaRepository = None):
        self.repo = repo or ProfilDesaRepository()

    # features/profil_wilayah/services.py
# Tidak perlu lagi mengimpor sanitize_html atau bleach di sini!

    def perbarui_profil(self, actor, visi: str, misi: str, sejarah: str):
        if not can_manage_data_wilayah(actor):
            raise ProfilWilayahAccessError("Akses ditolak.")
            
        # domain validation tetap berjalan
        validate_profil_desa(visi, misi, sejarah) 
        
        # Data visi, misi, sejarah sudah otomatis ter-sanitasi oleh Pydantic Schema!
        profil = self.repo.update_profil(visi, misi, sejarah)
        audit_event("PROFIL_DESA_UPDATED", actor_id=actor.id)
        return profil

    def get_profil(self):
        return self.repo.get_profil()