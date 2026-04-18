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