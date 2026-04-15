# features/auth_warga/tests/test_services.py

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from features.auth_warga.domain import (
    AuthenticationFailedError,
    DuplicateNIKError,
    InactiveAccountError,
    InvalidNIKError,
    InvalidRoleError,
    ROLE_ADMIN,
    ROLE_BUMDES,
    ROLE_SUPERADMIN,
    ROLE_WARGA,
)
from features.auth_warga.services import (
    AuthService,
    PermissionDeniedError,
    UserNotFoundError,
)

User = get_user_model()


@pytest.mark.django_db
def test_login_user_success():
    user = User.objects.create_user(
        nik="1234567890123456",
        password="password123",
        nama_lengkap="Budi",
        role=ROLE_WARGA,
    )

    request = RequestFactory().post("/api/auth/login/")
    service = AuthService()
    result = service.login_user(
        request=request,
        nik="1234567890123456",
        password="password123",
    )

    assert result.user.id == user.id


@pytest.mark.django_db
def test_login_user_wrong_password():
    User.objects.create_user(
        nik="1234567890123456",
        password="password123",
        nama_lengkap="Budi",
        role=ROLE_WARGA,
    )

    request = RequestFactory().post("/api/auth/login/")
    service = AuthService()
    with pytest.raises(AuthenticationFailedError):
        service.login_user(
            request=request,
            nik="1234567890123456",
            password="salah",
        )


@pytest.mark.django_db
def test_login_user_inactive_account():
    User.objects.create_user(
        nik="1234567890123456",
        password="password123",
        nama_lengkap="Budi",
        role=ROLE_WARGA,
        is_active=False,
    )

    request = RequestFactory().post("/api/auth/login/")
    service = AuthService()
    with pytest.raises(InactiveAccountError):
        service.login_user(
            request=request,
            nik="1234567890123456",
            password="password123",
        )


@pytest.mark.django_db
def test_login_user_invalid_nik_raises_error():
    request = RequestFactory().post("/api/auth/login/")
    service = AuthService()

    with pytest.raises(InvalidNIKError):
        service.login_user(
            request=request,
            nik="123",
            password="password123",
        )


@pytest.mark.django_db
def test_login_user_not_found_raises_authentication_failed():
    request = RequestFactory().post("/api/auth/login/")
    service = AuthService()

    with pytest.raises(AuthenticationFailedError):
        service.login_user(
            request=request,
            nik="1234567890123456",
            password="password123",
        )


@pytest.mark.django_db
def test_admin_can_deactivate_warga():
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
        nama_lengkap="Warga",
        role=ROLE_WARGA,
    )

    service = AuthService()
    service.deactivate_account(actor=actor, target_user_id=target.id)

    target.refresh_from_db()
    assert target.is_active is False


@pytest.mark.django_db
def test_admin_can_activate_warga():
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
        nama_lengkap="Warga",
        role=ROLE_WARGA,
        is_active=False,
    )

    service = AuthService()
    service.activate_account(actor=actor, target_user_id=target.id)

    target.refresh_from_db()
    assert target.is_active is True


@pytest.mark.django_db
def test_admin_cannot_deactivate_self():
    actor = User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="Admin",
        role=ROLE_ADMIN,
        is_staff=True,
    )

    service = AuthService()
    with pytest.raises(PermissionDeniedError):
        service.deactivate_account(actor=actor, target_user_id=actor.id)


@pytest.mark.django_db
def test_activate_account_user_not_found():
    actor = User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="Admin",
        role=ROLE_ADMIN,
        is_staff=True,
    )

    service = AuthService()
    with pytest.raises(UserNotFoundError):
        service.activate_account(actor=actor, target_user_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


@pytest.mark.django_db
def test_admin_cannot_manage_admin_account():
    actor = User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="Admin 1",
        role=ROLE_ADMIN,
        is_staff=True,
    )
    target = User.objects.create_user(
        nik="2222222222222222",
        password="password123",
        nama_lengkap="Admin 2",
        role=ROLE_ADMIN,
        is_staff=True,
        is_active=False,
    )

    service = AuthService()
    with pytest.raises(PermissionDeniedError):
        service.activate_account(actor=actor, target_user_id=target.id)


@pytest.mark.django_db
def test_admin_can_create_warga_account():
    actor = User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="Admin",
        role=ROLE_ADMIN,
        is_staff=True,
    )

    service = AuthService()
    created = service.create_warga_account(
        actor=actor,
        nik="2222222222222222",
        password="password123",
        nama_lengkap="Warga Baru",
    )

    assert created.role == ROLE_WARGA
    assert created.is_active is True
    assert created.is_staff is False


@pytest.mark.django_db
def test_warga_cannot_create_warga_account():
    actor = User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="Warga",
        role=ROLE_WARGA,
    )

    service = AuthService()
    with pytest.raises(PermissionDeniedError):
        service.create_warga_account(
            actor=actor,
            nik="2222222222222222",
            password="password123",
            nama_lengkap="Warga Baru",
        )


@pytest.mark.django_db
def test_create_warga_account_rejects_duplicate_nik():
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

    service = AuthService()
    with pytest.raises(DuplicateNIKError):
        service.create_warga_account(
            actor=actor,
            nik="2222222222222222",
            password="password123",
            nama_lengkap="Warga Baru",
        )


@pytest.mark.django_db
def test_superadmin_can_create_admin_account():
    actor = User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="Super Admin",
        role=ROLE_SUPERADMIN,
        is_staff=True,
        is_superuser=True,
    )

    service = AuthService()
    created = service.create_admin_account(
        actor=actor,
        nik="2222222222222222",
        password="password123",
        nama_lengkap="Admin Baru",
        role=ROLE_ADMIN,
    )

    assert created.role == ROLE_ADMIN
    assert created.is_staff is True
    assert created.is_active is True


@pytest.mark.django_db
def test_superadmin_can_create_bumdes_account():
    actor = User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="Super Admin",
        role=ROLE_SUPERADMIN,
        is_staff=True,
        is_superuser=True,
    )

    service = AuthService()
    created = service.create_admin_account(
        actor=actor,
        nik="3333333333333333",
        password="password123",
        nama_lengkap="BUMDes Baru",
        role=ROLE_BUMDES,
    )

    assert created.role == ROLE_BUMDES
    assert created.is_staff is True


@pytest.mark.django_db
def test_admin_cannot_create_admin_account():
    actor = User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="Admin",
        role=ROLE_ADMIN,
        is_staff=True,
    )

    service = AuthService()
    with pytest.raises(PermissionDeniedError):
        service.create_admin_account(
            actor=actor,
            nik="2222222222222222",
            password="password123",
            nama_lengkap="Admin Baru",
            role=ROLE_ADMIN,
        )


@pytest.mark.django_db
def test_create_admin_account_rejects_invalid_role():
    actor = User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="Super Admin",
        role=ROLE_SUPERADMIN,
        is_staff=True,
        is_superuser=True,
    )

    service = AuthService()
    with pytest.raises(InvalidRoleError):
        service.create_admin_account(
            actor=actor,
            nik="2222222222222222",
            password="password123",
            nama_lengkap="Role Salah",
            role="KEPALA_SEKSI",
        )


@pytest.mark.django_db
def test_create_admin_account_rejects_role_warga():
    actor = User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="Super Admin",
        role=ROLE_SUPERADMIN,
        is_staff=True,
        is_superuser=True,
    )

    service = AuthService()
    with pytest.raises(InvalidRoleError):
        service.create_admin_account(
            actor=actor,
            nik="2222222222222222",
            password="password123",
            nama_lengkap="Bukan Admin",
            role=ROLE_WARGA,
        )