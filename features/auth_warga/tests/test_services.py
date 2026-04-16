# features/auth_warga/tests/test_services.py
import uuid
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
class TestLoginService:

    def test_should_login_successfully_with_valid_credentials(self):
        """Login berhasil dengan NIK & password valid"""
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

    def test_should_fail_login_when_password_is_wrong(self):
        """Login gagal jika password salah"""
        User.objects.create_user(
            nik="1234567890123456",
            password="password123",
            nama_lengkap="Budi",
            role=ROLE_WARGA,
        )

        request = RequestFactory().post("/api/auth/login/")
        service = AuthService()

        with pytest.raises(AuthenticationFailedError):
            service.login_user(request=request, nik="1234567890123456", password="salah")

    def test_should_fail_login_when_account_is_inactive(self):
        """Login gagal jika akun tidak aktif"""
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
            service.login_user(request=request, nik="1234567890123456", password="password123")

    def test_should_fail_login_when_nik_is_invalid(self):
        """Login gagal jika format NIK tidak valid"""
        request = RequestFactory().post("/api/auth/login/")
        service = AuthService()

        with pytest.raises(InvalidNIKError):
            service.login_user(request=request, nik="123", password="password123")

    def test_should_fail_login_when_user_not_found(self):
        """Login gagal jika user tidak ditemukan"""
        request = RequestFactory().post("/api/auth/login/")
        service = AuthService()

        with pytest.raises(AuthenticationFailedError):
            service.login_user(request=request, nik="1234567890123456", password="password123")


@pytest.mark.django_db
class TestAccountActivationService:

    def test_should_allow_admin_to_deactivate_warga_account(self):
        """Admin boleh menonaktifkan akun warga"""
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

    def test_should_allow_admin_to_activate_warga_account(self):
        """Admin boleh mengaktifkan akun warga"""
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

    def test_should_prevent_admin_from_deactivating_self(self):
        """Admin tidak boleh menonaktifkan dirinya sendiri"""
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

    def test_should_raise_error_when_target_user_not_found(self):
        """Harus error jika user target tidak ditemukan"""
        actor = User.objects.create_user(
            nik="1111111111111111",
            password="password123",
            nama_lengkap="Admin",
            role=ROLE_ADMIN,
            is_staff=True,
        )

        service = AuthService()

        with pytest.raises(UserNotFoundError):
            service.activate_account(actor=actor, target_user_id=uuid.uuid4())

    def test_should_prevent_admin_from_managing_other_admin_accounts(self):
        """Admin tidak boleh manage admin lain"""
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
class TestWargaAccountCreationService:

    def test_should_allow_admin_to_create_warga_account(self):
        """Admin boleh membuat akun warga"""
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

    def test_should_prevent_warga_from_creating_warga_account(self):
        """Warga tidak boleh membuat akun warga"""
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

    def test_should_reject_duplicate_nik_when_creating_warga(self):
        """Harus error jika NIK sudah terdaftar"""
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
class TestAdminAccountCreationService:

    def test_should_allow_superadmin_to_create_admin_account(self):
        """Superadmin boleh membuat admin"""
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

    def test_should_allow_superadmin_to_create_bumdes_account(self):
        """Superadmin boleh membuat akun BUMDES"""
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

    def test_should_prevent_admin_from_creating_admin_account(self):
        """Admin tidak boleh membuat admin lain"""
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

    def test_should_reject_invalid_role_when_creating_admin(self):
        """Harus error jika role tidak valid"""
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

    def test_should_reject_warga_role_when_creating_admin(self):
        """Role WARGA tidak boleh digunakan untuk create admin"""
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