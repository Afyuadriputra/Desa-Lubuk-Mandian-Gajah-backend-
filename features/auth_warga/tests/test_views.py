# features/auth_warga/tests/test_views.py

import json
import uuid
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from features.auth_warga.domain import ROLE_ADMIN, ROLE_SUPERADMIN, ROLE_WARGA

User = get_user_model()


@pytest.mark.django_db
class TestLoginView:

    def test_should_return_200_when_login_successful(self):
        """Login berhasil dengan kredensial valid"""
        client = Client()
        User.objects.create_user(
            nik="1234567890123456",
            password="password123",
            nama_lengkap="Budi",
            role=ROLE_WARGA,
        )

        response = client.post(
            reverse("auth-login"),
            data=json.dumps({"nik": "1234567890123456", "password": "password123"}),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert response.json()["data"]["nik"] == "1234567890123456"

    def test_should_return_400_when_payload_invalid(self):
        """Harus 400 jika payload bukan JSON"""
        client = Client()

        response = client.post(
            reverse("auth-login"),
            data="bukan-json",
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_should_return_400_when_required_fields_missing(self):
        """Harus 400 jika field tidak lengkap"""
        client = Client()

        response = client.post(
            reverse("auth-login"),
            data=json.dumps({"nik": ""}),
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_should_return_400_when_nik_invalid(self):
        """Harus 400 jika format NIK salah"""
        client = Client()

        response = client.post(
            reverse("auth-login"),
            data=json.dumps({"nik": "123", "password": "password123"}),
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_should_return_403_when_account_inactive(self):
        """Harus 403 jika akun nonaktif"""
        client = Client()
        User.objects.create_user(
            nik="1234567890123456",
            password="password123",
            nama_lengkap="Budi",
            role=ROLE_WARGA,
            is_active=False,
        )

        response = client.post(
            reverse("auth-login"),
            data=json.dumps({"nik": "1234567890123456", "password": "password123"}),
            content_type="application/json",
        )

        assert response.status_code == 403

    def test_should_return_401_when_password_wrong(self):
        """Harus 401 jika password salah"""
        client = Client()
        User.objects.create_user(
            nik="1234567890123456",
            password="password123",
            nama_lengkap="Budi",
            role=ROLE_WARGA,
        )

        response = client.post(
            reverse("auth-login"),
            data=json.dumps({"nik": "1234567890123456", "password": "salah"}),
            content_type="application/json",
        )

        assert response.status_code == 401


@pytest.mark.django_db
class TestMeView:

    def test_should_return_401_when_not_authenticated(self):
        """Endpoint /me harus butuh login"""
        client = Client()
        response = client.get(reverse("auth-me"))
        assert response.status_code == 401

    def test_should_return_user_data_when_authenticated(self):
        """Harus return data user jika sudah login"""
        client = Client()
        user = User.objects.create_user(
            nik="1234567890123456",
            password="password123",
            nama_lengkap="Budi",
            role=ROLE_WARGA,
        )

        client.force_login(user)
        response = client.get(reverse("auth-me"))

        assert response.status_code == 200
        assert response.json()["data"]["nik"] == "1234567890123456"


@pytest.mark.django_db
class TestCreateWargaUserView:

    def test_should_return_401_when_not_authenticated(self):
        """Harus login untuk create warga"""
        client = Client()

        response = client.post(
            reverse("auth-create-warga-user"),
            data=json.dumps({
                "nik": "2222222222222222",
                "password": "password123",
                "nama_lengkap": "Warga Baru",
            }),
            content_type="application/json",
        )

        assert response.status_code == 401

    def test_should_allow_admin_to_create_warga(self):
        """Admin boleh create warga"""
        client = Client()
        actor = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="Admin",
            role=ROLE_ADMIN,
            is_staff=True,
        )

        client.force_login(actor)
        response = client.post(
            reverse("auth-create-warga-user"),
            data=json.dumps({
                "nik": "2222222222222222",
                "password": "password123",
                "nama_lengkap": "Warga Baru",
            }),
            content_type="application/json",
        )

        assert response.status_code == 201
        assert response.json()["data"]["role"] == ROLE_WARGA

    def test_should_return_400_when_nik_duplicate(self):
        """Harus 400 jika NIK sudah ada"""
        client = Client()
        actor = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="Admin",
            role=ROLE_ADMIN,
            is_staff=True,
        )
        User.objects.create_user(
            nik="2222222222222222",
            password="password123",
            nama_lengkap="Warga Lama",
            role=ROLE_WARGA,
        )

        client.force_login(actor)
        response = client.post(
            reverse("auth-create-warga-user"),
            data=json.dumps({
                "nik": "2222222222222222",
                "password": "password123",
                "nama_lengkap": "Warga Baru",
            }),
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_should_return_403_when_warga_create_warga(self):
        """Warga tidak boleh create warga"""
        client = Client()
        actor = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="Warga",
            role=ROLE_WARGA,
        )

        client.force_login(actor)
        response = client.post(
            reverse("auth-create-warga-user"),
            data=json.dumps({
                "nik": "2222222222222222",
                "password": "password123",
                "nama_lengkap": "Warga Baru",
            }),
            content_type="application/json",
        )

        assert response.status_code == 403


@pytest.mark.django_db
class TestCreateAdminUserView:

    def test_should_return_401_when_not_authenticated(self):
        client = Client()

        response = client.post(
            reverse("auth-create-admin-user"),
            data=json.dumps({
                "nik": "2222222222222222",
                "password": "password123",
                "nama_lengkap": "Admin Baru",
                "role": ROLE_ADMIN,
            }),
            content_type="application/json",
        )

        assert response.status_code == 401

    def test_should_allow_superadmin_to_create_admin(self):
        client = Client()
        actor = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="Super Admin",
            role=ROLE_SUPERADMIN,
            is_staff=True,
            is_superuser=True,
        )

        client.force_login(actor)
        response = client.post(
            reverse("auth-create-admin-user"),
            data=json.dumps({
                "nik": "2222222222222222",
                "password": "password123",
                "nama_lengkap": "Admin Baru",
                "role": ROLE_ADMIN,
            }),
            content_type="application/json",
        )

        assert response.status_code == 201
        assert response.json()["data"]["role"] == ROLE_ADMIN

    def test_should_return_403_when_admin_create_admin(self):
        client = Client()
        actor = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="Admin",
            role=ROLE_ADMIN,
            is_staff=True,
        )

        client.force_login(actor)
        response = client.post(
            reverse("auth-create-admin-user"),
            data=json.dumps({
                "nik": "2222222222222222",
                "password": "password123",
                "nama_lengkap": "Admin Baru",
                "role": ROLE_ADMIN,
            }),
            content_type="application/json",
        )

        assert response.status_code == 403

    def test_should_return_400_when_role_invalid(self):
        client = Client()
        actor = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="Super Admin",
            role=ROLE_SUPERADMIN,
            is_staff=True,
            is_superuser=True,
        )

        client.force_login(actor)
        response = client.post(
            reverse("auth-create-admin-user"),
            data=json.dumps({
                "nik": "2222222222222222",
                "password": "password123",
                "nama_lengkap": "Role Salah",
                "role": "KEPALA_SEKSI",
            }),
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_should_return_400_when_role_is_warga(self):
        client = Client()
        actor = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="Super Admin",
            role=ROLE_SUPERADMIN,
            is_staff=True,
            is_superuser=True,
        )

        client.force_login(actor)
        response = client.post(
            reverse("auth-create-admin-user"),
            data=json.dumps({
                "nik": "2222222222222222",
                "password": "password123",
                "nama_lengkap": "Bukan Admin",
                "role": ROLE_WARGA,
            }),
            content_type="application/json",
        )

        assert response.status_code == 400


@pytest.mark.django_db
class TestActivationView:

    def test_should_return_403_when_user_has_no_permission(self):
        client = Client()

        actor = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="Warga",
            role=ROLE_WARGA,
        )
        target = User.objects.create_user(
            nik="2222222222222222",
            password="password123",
            nama_lengkap="Target",
            role=ROLE_WARGA,
            is_active=False,
        )

        client.force_login(actor)
        response = client.post(reverse("auth-activate-user", kwargs={"user_id": str(target.id)}))

        assert response.status_code == 403

    def test_should_allow_admin_to_activate_warga(self):
        client = Client()

        actor = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="Admin",
            role=ROLE_ADMIN,
            is_staff=True,
        )
        target = User.objects.create_user(
            nik="2222222222222222",
            password="password123",
            nama_lengkap="Target",
            role=ROLE_WARGA,
            is_active=False,
        )

        client.force_login(actor)
        response = client.post(reverse("auth-activate-user", kwargs={"user_id": str(target.id)}))

        assert response.status_code == 200
        target.refresh_from_db()
        assert target.is_active is True

    def test_should_return_404_when_deactivate_user_not_found(self):
        client = Client()

        actor = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="Admin",
            role=ROLE_ADMIN,
            is_staff=True,
        )

        client.force_login(actor)
        response = client.post(
            reverse("auth-deactivate-user", kwargs={"user_id": str(uuid.uuid4())})
        )

        assert response.status_code == 404