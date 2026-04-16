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
class TestUserManagementPermissions:

    def test_should_allow_superadmin_to_manage_admin_accounts(self):
        """SUPERADMIN boleh activate & deactivate akun admin"""
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

    def test_should_prevent_admin_from_managing_other_admin_accounts(self):
        """ADMIN tidak boleh manage admin lain"""
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

    def test_should_allow_admin_to_manage_warga_accounts(self):
        """ADMIN boleh manage akun warga"""
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
class TestSelfPermissions:

    def test_should_allow_user_to_view_own_account(self):
        """User boleh melihat dirinya sendiri"""
        actor = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="User 1",
            role=ROLE_WARGA,
        )

        assert can_view_self(actor, actor) is True

    def test_should_prevent_user_from_deactivating_self(self):
        """User tidak boleh menonaktifkan dirinya sendiri"""
        actor = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="Admin",
            role=ROLE_ADMIN,
            is_staff=True,
        )

        assert can_deactivate_user(actor, actor) is False


@pytest.mark.django_db
class TestUserCreationPermissions:

    def test_should_allow_superadmin_to_create_admin_user(self):
        """SUPERADMIN boleh membuat akun admin"""
        actor = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="Super Admin",
            role=ROLE_SUPERADMIN,
            is_staff=True,
        )

        assert can_create_admin_user(actor) is True

    def test_should_prevent_admin_from_creating_admin_user(self):
        """ADMIN tidak boleh membuat admin lain"""
        actor = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="Admin",
            role=ROLE_ADMIN,
            is_staff=True,
        )

        assert can_create_admin_user(actor) is False

    def test_should_allow_admin_to_create_warga_user(self):
        """ADMIN boleh membuat akun warga"""
        actor = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="Admin",
            role=ROLE_ADMIN,
            is_staff=True,
        )

        assert can_create_warga_user(actor) is True

    def test_should_prevent_warga_from_creating_warga_user(self):
        """WARGA tidak boleh membuat akun warga lain"""
        actor = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="Warga",
            role=ROLE_WARGA,
        )

        assert can_create_warga_user(actor) is False