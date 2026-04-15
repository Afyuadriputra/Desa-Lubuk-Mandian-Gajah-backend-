# features/auth_warga/models.py

import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from features.auth_warga.domain import (
    ROLE_ADMIN,
    ROLE_BUMDES,
    ROLE_SUPERADMIN,
    ROLE_WARGA,
    normalize_nik,
    validate_nik,
    validate_role,
)


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(
        self,
        nik: str,
        password: str,
        nama_lengkap: str,
        role: str = ROLE_WARGA,
        **extra_fields,
    ):
        if not nik:
            raise ValueError("NIK wajib diisi.")
        if not password:
            raise ValueError("Password wajib diisi.")
        if not nama_lengkap:
            raise ValueError("Nama lengkap wajib diisi.")

        nik = normalize_nik(nik)
        validate_nik(nik)
        validate_role(role)

        user = self.model(
            nik=nik,
            nama_lengkap=nama_lengkap.strip(),
            role=role,
            **extra_fields,
        )
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_user(
        self,
        nik: str,
        password: str,
        nama_lengkap: str,
        role: str = ROLE_WARGA,
        **extra_fields,
    ):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(
            nik=nik,
            password=password,
            nama_lengkap=nama_lengkap,
            role=role,
            **extra_fields,
        )

    def create_superuser(
        self,
        nik: str,
        password: str,
        nama_lengkap: str,
        **extra_fields,
    ):
        extra_fields.setdefault("role", ROLE_SUPERADMIN)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields["is_staff"] is not True:
            raise ValueError("Superuser harus memiliki is_staff=True.")
        if extra_fields["is_superuser"] is not True:
            raise ValueError("Superuser harus memiliki is_superuser=True.")

        role = extra_fields.pop("role")
        validate_role(role)

        return self._create_user(
            nik=nik,
            password=password,
            nama_lengkap=nama_lengkap,
            role=role,
            **extra_fields,
        )


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        (ROLE_SUPERADMIN, "Super Admin"),
        (ROLE_ADMIN, "Admin Desa"),
        (ROLE_BUMDES, "Admin BUMDes"),
        (ROLE_WARGA, "Warga"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nik = models.CharField(max_length=16, unique=True, db_index=True)
    nama_lengkap = models.CharField(max_length=150)
    nomor_hp = models.CharField(max_length=20, blank=True, null=True)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_WARGA,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "nik"
    REQUIRED_FIELDS = ["nama_lengkap"]

    objects = CustomUserManager()

    class Meta:
        db_table = "users_customuser"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        self.nik = normalize_nik(self.nik)
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        self.nik = normalize_nik(self.nik)
        validate_nik(self.nik)
        validate_role(self.role)

    def __str__(self) -> str:
        return f"{self.nama_lengkap} ({self.nik})"