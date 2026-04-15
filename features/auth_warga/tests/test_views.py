# features/auth_warga/tests/test_views.py

import json

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from features.auth_warga.domain import ROLE_ADMIN, ROLE_SUPERADMIN, ROLE_WARGA

User = get_user_model()


@pytest.mark.django_db
def test_login_view_success():
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
    body = response.json()
    assert body["data"]["nik"] == "1234567890123456"


@pytest.mark.django_db
def test_login_view_invalid_payload_returns_400():
    client = Client()

    response = client.post(
        reverse("auth-login"),
        data="bukan-json",
        content_type="application/json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_login_view_missing_fields_returns_400():
    client = Client()

    response = client.post(
        reverse("auth-login"),
        data=json.dumps({"nik": ""}),
        content_type="application/json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_login_view_invalid_nik_returns_400():
    client = Client()

    response = client.post(
        reverse("auth-login"),
        data=json.dumps({"nik": "123", "password": "password123"}),
        content_type="application/json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_login_view_inactive_account_returns_403():
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


@pytest.mark.django_db
def test_login_view_wrong_password_returns_401():
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
def test_me_view_requires_authentication():
    client = Client()
    response = client.get(reverse("auth-me"))
    assert response.status_code == 401


@pytest.mark.django_db
def test_me_view_success():
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
    body = response.json()
    assert body["data"]["nik"] == "1234567890123456"


@pytest.mark.django_db
def test_create_warga_user_view_requires_authentication():
    client = Client()

    response = client.post(
        reverse("auth-create-warga-user"),
        data=json.dumps(
            {
                "nik": "2222222222222222",
                "password": "password123",
                "nama_lengkap": "Warga Baru",
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_create_warga_user_view_admin_success():
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
        data=json.dumps(
            {
                "nik": "2222222222222222",
                "password": "password123",
                "nama_lengkap": "Warga Baru",
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 201
    body = response.json()
    assert body["data"]["role"] == ROLE_WARGA


@pytest.mark.django_db
def test_create_warga_user_view_duplicate_nik_returns_400():
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
        data=json.dumps(
            {
                "nik": "2222222222222222",
                "password": "password123",
                "nama_lengkap": "Warga Baru",
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_create_warga_user_view_warga_forbidden():
    client = Client()

    actor = User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="Warga Aktor",
        role=ROLE_WARGA,
    )
    client.force_login(actor)

    response = client.post(
        reverse("auth-create-warga-user"),
        data=json.dumps(
            {
                "nik": "2222222222222222",
                "password": "password123",
                "nama_lengkap": "Warga Baru",
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_create_admin_user_view_requires_authentication():
    client = Client()

    response = client.post(
        reverse("auth-create-admin-user"),
        data=json.dumps(
            {
                "nik": "2222222222222222",
                "password": "password123",
                "nama_lengkap": "Admin Baru",
                "role": ROLE_ADMIN,
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_create_admin_user_view_superadmin_success():
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
        data=json.dumps(
            {
                "nik": "2222222222222222",
                "password": "password123",
                "nama_lengkap": "Admin Baru",
                "role": ROLE_ADMIN,
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 201
    body = response.json()
    assert body["data"]["role"] == ROLE_ADMIN


@pytest.mark.django_db
def test_create_admin_user_view_admin_forbidden():
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
        data=json.dumps(
            {
                "nik": "2222222222222222",
                "password": "password123",
                "nama_lengkap": "Admin Baru",
                "role": ROLE_ADMIN,
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_create_admin_user_view_invalid_role_returns_400():
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
        data=json.dumps(
            {
                "nik": "2222222222222222",
                "password": "password123",
                "nama_lengkap": "Role Salah",
                "role": "KEPALA_SEKSI",
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_create_admin_user_view_role_warga_returns_400():
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
        data=json.dumps(
            {
                "nik": "2222222222222222",
                "password": "password123",
                "nama_lengkap": "Bukan Admin",
                "role": ROLE_WARGA,
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_activate_user_requires_permission():
    client = Client()

    actor = User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="Warga Aktor",
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


@pytest.mark.django_db
def test_admin_can_activate_warga():
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


@pytest.mark.django_db
def test_deactivate_user_view_not_found_returns_404():
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
        reverse("auth-deactivate-user", kwargs={"user_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"})
    )

    assert response.status_code == 404