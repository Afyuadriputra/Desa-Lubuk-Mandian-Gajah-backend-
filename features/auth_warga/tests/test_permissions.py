# features/auth_warga/tests/test_permissions.py

import pytest
from django.contrib.auth import get_user_model

from features.auth_warga.domain import ROLE_ADMIN, ROLE_SUPERADMIN, ROLE_WARGA
from features.auth_warga.permissions import (
    can_activate_user,
    can_create_admin_user,
    can_create_warga_user,
    can_deactivate_user,
    can_view_self,
)

User = get_user_model()


@pytest.mark.django_db
def test_superadmin_can_manage_admin():
    actor = User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="Super Admin",
        role=ROLE_SUPERADMIN,
        is_staff=True,
    )
    target = User.objects.create_user(
        nik="2222222222222222",
        password="password123",
        nama_lengkap="Admin Desa",
        role=ROLE_ADMIN,
        is_staff=True,
    )

    assert can_activate_user(actor, target) is True
    assert can_deactivate_user(actor, target) is True


@pytest.mark.django_db
def test_admin_cannot_manage_admin():
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
    )

    assert can_activate_user(actor, target) is False
    assert can_deactivate_user(actor, target) is False


@pytest.mark.django_db
def test_admin_can_manage_warga():
    actor = User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="Admin",
        role=ROLE_ADMIN,
        is_staff=True,
    )
    target = User.objects.create_user(
        nik="3333333333333333",
        password="password123",
        nama_lengkap="Warga",
        role=ROLE_WARGA,
    )

    assert can_activate_user(actor, target) is True
    assert can_deactivate_user(actor, target) is True


@pytest.mark.django_db
def test_can_view_self_returns_true_for_same_user():
    actor = User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="User 1",
        role=ROLE_WARGA,
    )

    assert can_view_self(actor, actor) is True


@pytest.mark.django_db
def test_can_deactivate_user_returns_false_for_self():
    actor = User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="Admin",
        role=ROLE_ADMIN,
        is_staff=True,
    )

    assert can_deactivate_user(actor, actor) is False


@pytest.mark.django_db
def test_superadmin_can_create_admin_user():
    actor = User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="Super Admin",
        role=ROLE_SUPERADMIN,
        is_staff=True,
    )

    assert can_create_admin_user(actor) is True


@pytest.mark.django_db
def test_admin_cannot_create_admin_user():
    actor = User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="Admin",
        role=ROLE_ADMIN,
        is_staff=True,
    )

    assert can_create_admin_user(actor) is False


@pytest.mark.django_db
def test_admin_can_create_warga_user():
    actor = User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="Admin",
        role=ROLE_ADMIN,
        is_staff=True,
    )

    assert can_create_warga_user(actor) is True


@pytest.mark.django_db
def test_warga_cannot_create_warga_user():
    actor = User.objects.create_user(
        nik="1111111111111111",
        password="password123",
        nama_lengkap="Warga",
        role=ROLE_WARGA,
    )

    assert can_create_warga_user(actor) is False