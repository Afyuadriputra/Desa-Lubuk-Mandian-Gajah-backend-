# features/auth_warga/repositories.py

from django.db.models import QuerySet

from features.auth_warga.models import CustomUser


class UserRepository:
    def get_by_id(self, user_id) -> CustomUser | None:
        return CustomUser.objects.filter(id=user_id).first()

    def get_by_nik(self, nik: str) -> CustomUser | None:
        return CustomUser.objects.filter(nik=nik).first()

    def exists_by_nik(self, nik: str) -> bool:
        return CustomUser.objects.filter(nik=nik).exists()

    def list_all(self) -> QuerySet[CustomUser]:
        return CustomUser.objects.all()

    def list_by_role(self, role: str) -> QuerySet[CustomUser]:
        return CustomUser.objects.filter(role=role)

    def create_user(
        self,
        nik: str,
        password: str,
        nama_lengkap: str,
        role: str,
        nomor_hp: str | None = None,
        is_active: bool = True,
        is_staff: bool = False,
    ) -> CustomUser:
        return CustomUser.objects.create_user(
            nik=nik,
            password=password,
            nama_lengkap=nama_lengkap,
            role=role,
            nomor_hp=nomor_hp,
            is_active=is_active,
            is_staff=is_staff,
        )

    def save(self, user: CustomUser) -> CustomUser:
        user.save()
        return user

    def activate(self, user: CustomUser) -> CustomUser:
        user.is_active = True
        user.save(update_fields=["is_active", "updated_at"])
        return user

    def deactivate(self, user: CustomUser) -> CustomUser:
        user.is_active = False
        user.save(update_fields=["is_active", "updated_at"])
        return user

    def update_password(self, user: CustomUser, new_password: str) -> CustomUser:
        user.set_password(new_password)
        user.save(update_fields=["password", "updated_at"])
        return user
