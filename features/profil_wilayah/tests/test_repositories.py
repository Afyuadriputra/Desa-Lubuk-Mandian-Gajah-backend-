import pytest
from features.profil_wilayah.repositories import (
    DusunRepository,
    PerangkatRepository,
    ProfilDesaRepository,
)

pytestmark = pytest.mark.django_db

class TestProfilWilayahRepositories:
    def test_profil_desa_repo_harus_implementasi_singleton(self):
        """Memastikan get_profil() selalu mengembalikan record dengan ID=1 (YAGNI)."""
        repo = ProfilDesaRepository()
        
        profil_1 = repo.get_profil()
        profil_2 = repo.get_profil()
        
        assert profil_1.id == 1
        assert profil_1.id == profil_2.id

    def test_profil_desa_repo_harus_bisa_update_data(self):
        repo = ProfilDesaRepository()
        updated_profil = repo.update_profil(visi="Visi Baru", misi="Misi Baru", sejarah="Sejarah Baru")
        
        assert updated_profil.visi == "Visi Baru"
        
        # Pastikan data tersimpan di DB
        db_profil = repo.get_profil()
        assert db_profil.visi == "Visi Baru"

    def test_perangkat_repo_hanya_kembalikan_yang_dipublish(self, django_user_model):
        user = django_user_model.objects.create(nik="123", nama_lengkap="Warga")
        repo = PerangkatRepository()
        
        repo.create(user_id=user.id, jabatan="Kaur", is_published=True)
        repo.create(user_id=user.id, jabatan="Kasi", is_published=False)
        
        hasil = repo.list_published()
        assert hasil.count() == 1
        assert hasil.first().jabatan == "Kaur"