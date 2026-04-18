# LLM Context: Tests untuk fitur `profil_wilayah`

Dokumen ini berisi kumpulan kode dari direktori `profil_wilayah/tests` untuk keperluan konteks LLM.

---
## File: `profil_wilayah/tests/test_api.py`

```python
import pytest
import json
from features.profil_wilayah.models import ProfilDesa

@pytest.mark.django_db
class TestProfilWilayahAPI:

    def test_publik_bisa_akses_tanpa_login_dan_teragregasi(self, client):
        """KISS: Menguji bahwa endpoint /publik mengembalikan Profil dan Perangkat tanpa auth."""
        # Setup data
        ProfilDesa.objects.create(id=1, visi="Visi API", misi="Misi API", sejarah="Sejarah API")
        
        # Request tanpa force_login
        response = client.get("/api/v1/profil-wilayah/publik")
        
        assert response.status_code == 200
        data = response.json()
        
        # Cek struktur aggregated
        assert "profil" in data
        assert "perangkat" in data
        assert data["profil"]["visi"] == "Visi API"

    def test_update_profil_dengan_xss_otomatis_bersih(self, client, admin_user):
        """DRY: Menguji SafeHTMLString pada JSON Payload."""
        client.force_login(admin_user)
        
        # Pydantic via JSON body
        payload = {
            "visi": "<b>Visi Hebat</b>",
            "misi": "Misi Kuat",
            "sejarah": "<script>console.log('xss')</script> Sejarah lama"
        }

        response = client.put(
            "/api/v1/profil-wilayah/admin/profil", 
            data=json.dumps(payload), 
            content_type="application/json"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "<b>Visi Hebat</b>" in data["visi"]
        assert "<script>" not in data["sejarah"] # XSS hilang
        assert "Sejarah lama" in data["sejarah"]
```

---
## File: `profil_wilayah/tests/test_domain.py`

```python
import pytest
from features.profil_wilayah.domain import (
    InvalidDataError,
    validate_dusun,
    validate_perangkat,
    validate_profil_desa,
)

class TestDomainProfilWilayah:
    # --- Validasi Dusun ---
    def test_validasi_dusun_harus_sukses_jika_data_valid(self):
        validate_dusun(nama_dusun="Mawar", kepala_dusun="Pak Budi")  # Tidak boleh error

    def test_validasi_dusun_harus_gagal_jika_nama_terlalu_pendek(self):
        with pytest.raises(InvalidDataError, match="minimal 3 karakter"):
            validate_dusun(nama_dusun="AB", kepala_dusun="Pak Budi")

    def test_validasi_dusun_harus_gagal_jika_kepala_dusun_kosong(self):
        with pytest.raises(InvalidDataError, match="kepala dusun wajib diisi"):
            validate_dusun(nama_dusun="Melati", kepala_dusun="   ")

    # --- Validasi Perangkat ---
    def test_validasi_perangkat_harus_sukses_jika_jabatan_valid(self):
        validate_perangkat(jabatan="Sekretaris Desa")

    def test_validasi_perangkat_harus_gagal_jika_jabatan_kosong(self):
        with pytest.raises(InvalidDataError, match="Jabatan wajib diisi"):
            validate_perangkat(jabatan="")

    # --- Validasi Profil Desa ---
    def test_validasi_profil_desa_harus_sukses_jika_lengkap(self):
        validate_profil_desa(visi="Maju", misi="Bersama", sejarah="Tahun 1990")

    def test_validasi_profil_desa_harus_gagal_jika_ada_yang_kosong(self):
        with pytest.raises(InvalidDataError, match="tidak boleh kosong"):
            validate_profil_desa(visi="Maju", misi="", sejarah="Tahun 1990")
```

---
## File: `profil_wilayah/tests/test_repositories.py`

```python
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
```

---
## File: `profil_wilayah/tests/test_services.py`

```python
import pytest
from features.profil_wilayah.services import (
    DusunService,
    ProfilWilayahAccessError,
)

class TestDusunService:
    @pytest.fixture
    def mock_repo(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def service(self, mock_repo):
        # Menerapkan Dependency Inversion dengan meng-inject Mock Repository
        return DusunService(repo=mock_repo)

    @pytest.fixture
    def mock_admin(self, mocker):
        user = mocker.Mock(id=1, role="ADMIN")
        return user

    def test_tambah_dusun_harus_sukses_untuk_admin(self, service, mock_admin, mock_repo, mocker):
        # Arrange
        mocker.patch("features.profil_wilayah.services.can_manage_data_wilayah", return_value=True)
        mock_audit = mocker.patch("features.profil_wilayah.services.audit_event")
        mock_repo.create.return_value = mocker.Mock(id=10)

        # Act
        hasil = service.tambah_dusun(mock_admin, nama_dusun="Mawar", kepala_dusun="Budi")

        # Assert
        assert hasil.id == 10
        mock_repo.create.assert_called_once_with("Mawar", "Budi")
        mock_audit.assert_called_once_with("DUSUN_CREATED", actor_id=1, target_id=10)

    def test_tambah_dusun_harus_ditolak_jika_tidak_punya_izin(self, service, mock_admin, mocker):
        mocker.patch("features.profil_wilayah.services.can_manage_data_wilayah", return_value=False)

        with pytest.raises(ProfilWilayahAccessError, match="Akses ditolak"):
            service.tambah_dusun(mock_admin, nama_dusun="Mawar", kepala_dusun="Budi")
```

---
## File: `profil_wilayah/tests/__init__.py`

```python

```

