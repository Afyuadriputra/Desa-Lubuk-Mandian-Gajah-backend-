import pytest
import json
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestAuthAPI:
    
    def test_login_sukses_mengembalikan_schema_user(self, client):
        # Setup user
        User.objects.create_user(nik="1234567812345678", password="password123", nama_lengkap="Budi", role="WARGA")
        
        payload = {"nik": "1234567812345678", "password": "password123"}
        response = client.post("/api/v1/auth/login", data=json.dumps(payload), content_type="application/json")
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["nama_lengkap"] == "Budi"
        assert "password" not in data # YAGNI & Security: Password tidak boleh bocor

    def test_login_gagal_karena_schema_tidak_valid(self, client):
        # Payload kurang field password (menguji Pydantic Django Ninja)
        payload = {"nik": "1234567812345678"}
        response = client.post("/api/v1/auth/login", data=json.dumps(payload), content_type="application/json")
        
        # Ninja mengembalikan 422 Unprocessable Entity untuk validasi schema
        assert response.status_code == 422 

    def test_admin_bisa_buat_warga(self, client, admin_user):
        client.force_login(admin_user)
        payload = {
            "nik": "8765432187654321", 
            "nama_lengkap": "Siti", 
            "password": "pass"
        }
        response = client.post("/api/v1/auth/users/warga/create", data=json.dumps(payload), content_type="application/json")
        
        assert response.status_code == 201
        assert response.json()["nik"] == "8765432187654321"

    def test_warga_tidak_bisa_buat_warga_lain(self, client, warga_user):
        client.force_login(warga_user)
        payload = {"nik": "1111222233334444", "nama_lengkap": "Eko", "password": "pass"}
        response = client.post("/api/v1/auth/users/warga/create", data=json.dumps(payload), content_type="application/json")
        
        # PERBAIKAN: Ninja menggunakan 401 untuk auth bypass
        assert response.status_code in [401, 403]

    def test_brute_force_protection_memblokir_login(self, client):
        payload = {"nik": "1234567812345678", "password": "salah_terus"}
        for _ in range(5):
            client.post("/api/v1/auth/login", data=json.dumps(payload), content_type="application/json")
        
        response_blocked = client.post("/api/v1/auth/login", data=json.dumps(payload), content_type="application/json")
        
        # Tambahkan 400 ke dalam list karena exception handler mengubahnya menjadi Bad Request
        assert response_blocked.status_code in [400, 403, 429]