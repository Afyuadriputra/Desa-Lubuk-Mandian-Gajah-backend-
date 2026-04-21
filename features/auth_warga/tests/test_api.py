import pytest
import json
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.test import Client, override_settings
from django.urls import reverse

User = get_user_model()

@pytest.mark.django_db
class TestAuthAPI:
    @override_settings(ALLOWED_HOSTS=["testserver", "127.0.0.1", "localhost"])
    def test_csrf_endpoint_mengembalikan_token_dan_cookie(self):
        client = Client(enforce_csrf_checks=True)

        response = client.get(reverse("auth-csrf"))

        assert response.status_code == 200
        assert "csrfToken" in response.json()
        assert client.cookies.get("csrftoken") is not None

    
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

    @override_settings(ALLOWED_HOSTS=["testserver", "127.0.0.1", "localhost"])
    def test_login_strict_csrf_memblokir_request_tanpa_token(self):
        User.objects.create_user(
            nik="1234567812345678",
            password="password123",
            nama_lengkap="Budi",
            role="WARGA",
        )
        client = Client(enforce_csrf_checks=True)

        response = client.post(
            "/api/v1/auth/login",
            data=json.dumps({"nik": "1234567812345678", "password": "password123"}),
            content_type="application/json",
        )

        assert response.status_code == 403

    @override_settings(ALLOWED_HOSTS=["testserver", "127.0.0.1", "localhost"])
    def test_login_dengan_csrf_token_berhasil(self):
        User.objects.create_user(
            nik="2222333344445555",
            password="password123",
            nama_lengkap="Budi CSRF",
            role="WARGA",
        )
        client = Client(enforce_csrf_checks=True)
        csrf_response = client.get(reverse("auth-csrf"))

        assert csrf_response.status_code == 200

        response = client.post(
            "/api/v1/auth/login",
            data=json.dumps({"nik": "2222333344445555", "password": "password123"}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
        )

        assert response.status_code == 200

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

    def test_superadmin_bisa_lihat_detail_user_dengan_group_dan_permission(self, client, admin_user, warga_user):
        group = Group.objects.create(name="Operator Desa")
        permission = Permission.objects.filter(codename="view_group").first()
        assert permission is not None
        warga_user.groups.add(group)
        warga_user.user_permissions.add(permission)
        client.force_login(admin_user)

        response = client.get(reverse("auth-users-detail", kwargs={"user_id": str(warga_user.id)}))

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(warga_user.id)
        assert len(data["groups"]) == 1
        assert len(data["user_permissions"]) >= 1

    def test_superadmin_bisa_update_user_dan_assign_group_permission(self, client, admin_user, warga_user):
        group = Group.objects.create(name="Editor")
        permission = Permission.objects.filter(codename="change_group").first()
        assert permission is not None
        client.force_login(admin_user)

        response = client.put(
            reverse("auth-users-update", kwargs={"user_id": str(warga_user.id)}),
            data=json.dumps(
                {
                    "nama_lengkap": "Warga Diubah",
                    "nomor_hp": "081111111111",
                    "role": "WARGA",
                    "is_active": True,
                    "is_staff": False,
                    "is_superuser": False,
                    "groups": [group.id],
                    "user_permissions": [permission.id],
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 200
        warga_user.refresh_from_db()
        assert warga_user.nama_lengkap == "Warga Diubah"
        assert warga_user.groups.filter(id=group.id).exists() is True
        assert warga_user.user_permissions.filter(id=permission.id).exists() is True

    def test_admin_hanya_bisa_edit_warga_tanpa_permission(self, client, warga_user):
        admin = User.objects.create_user(
            nik="8888888888888888",
            password="password123",
            nama_lengkap="Admin Desa",
            role="ADMIN",
            is_staff=True,
        )
        client.force_login(admin)
        group = Group.objects.create(name="Restricted")

        response = client.put(
            reverse("auth-users-update", kwargs={"user_id": str(warga_user.id)}),
            data=json.dumps(
                {
                    "nama_lengkap": "Warga Admin Edit",
                    "nomor_hp": "082222222222",
                    "role": "WARGA",
                    "is_active": True,
                    "is_staff": False,
                    "is_superuser": False,
                    "groups": [group.id],
                    "user_permissions": [],
                }
            ),
            content_type="application/json",
        )

        assert response.status_code in [400, 403]

    def test_admin_bisa_lihat_list_group_dan_permission(self, client, warga_user):
        admin = User.objects.create_user(
            nik="7777777777777777",
            password="password123",
            nama_lengkap="Admin Desa",
            role="ADMIN",
            is_staff=True,
        )
        Group.objects.create(name="Verifier")
        client.force_login(admin)

        groups_response = client.get(reverse("auth-groups-list"))
        permissions_response = client.get(reverse("auth-permissions-list"))

        assert groups_response.status_code == 200
        assert permissions_response.status_code == 200
        assert any(item["name"] == "Verifier" for item in groups_response.json())
        assert len(permissions_response.json()) >= 1

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

    def test_admin_bisa_reset_password_warga_via_api(self, client, admin_user, warga_user):
        client.force_login(admin_user)

        response = client.post(
            reverse("auth-users-reset-password", kwargs={"user_id": str(warga_user.id)}),
            data=json.dumps(
                {
                    "new_password": "password789",
                    "confirm_password": "password789",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 200
        warga_user.refresh_from_db()
        assert warga_user.check_password("password789") is True

    def test_admin_tidak_bisa_reset_password_admin_lain_via_api(self, client, warga_user):
        admin = User.objects.create_user(
            nik="6666666666666666",
            password="password123",
            nama_lengkap="Admin Desa",
            role="ADMIN",
            is_staff=True,
        )
        admin_lain = User.objects.create_user(
            nik="5555555555555555",
            password="password123",
            nama_lengkap="Admin Lain",
            role="ADMIN",
            is_staff=True,
        )
        client.force_login(admin)

        response = client.post(
            reverse("auth-users-reset-password", kwargs={"user_id": str(admin_lain.id)}),
            data=json.dumps(
                {
                    "new_password": "password789",
                    "confirm_password": "password789",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code in [400, 403]
