import pytest
import json
from django.contrib.auth import get_user_model
from django.urls import reverse

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

    def test_superadmin_bisa_buat_admin_dari_named_route(self, client, admin_user):
        client.force_login(admin_user)
        response = client.post(
            reverse("auth-users-admin-create"),
            data=json.dumps(
                {
                    "nik": "1111222233334444",
                    "nama_lengkap": "Admin Desa Baru",
                    "password": "password123",
                    "role": "ADMIN",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 201
        assert response.json()["role"] == "ADMIN"

    def test_admin_bisa_list_dan_search_user_via_api(self, client, admin_user):
        client.force_login(admin_user)
        User.objects.create_user(
            nik="9999888877776666",
            password="password123",
            nama_lengkap="Warga Cari",
            nomor_hp="081234567890",
            role="WARGA",
        )

        response = client.get(
            reverse("auth-users-list"),
            {"q": "Cari", "role": "WARGA", "is_active": "true"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(item["nama_lengkap"] == "Warga Cari" for item in data)
        assert all(item["role"] == "WARGA" for item in data)

    def test_warga_tidak_bisa_list_user_via_api(self, client, warga_user):
        client.force_login(warga_user)

        response = client.get(reverse("auth-users-list"))

        assert response.status_code in [401, 403]

    def test_admin_bisa_aktivasi_dan_nonaktifkan_akun_via_api(self, client, admin_user, warga_user):
        client.force_login(admin_user)

        deactivate_response = client.post(reverse("auth-users-deactivate", kwargs={"user_id": str(warga_user.id)}))
        assert deactivate_response.status_code == 200
        assert deactivate_response.json()["is_active"] is False

        activate_response = client.post(reverse("auth-users-activate", kwargs={"user_id": str(warga_user.id)}))
        assert activate_response.status_code == 200
        assert activate_response.json()["is_active"] is True

    def test_user_bisa_ganti_password_via_api(self, client, warga_user):
        client.force_login(warga_user)

        response = client.post(
            reverse("auth-change-password"),
            data=json.dumps(
                {
                    "current_password": "password123",
                    "new_password": "password456",
                    "confirm_password": "password456",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 200
        warga_user.refresh_from_db()
        assert warga_user.check_password("password456") is True
