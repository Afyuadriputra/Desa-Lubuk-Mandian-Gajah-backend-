# features/auth_warga/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from features.auth_warga.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    ordering = ("-created_at",)
    list_display = (
        "nik",
        "nama_lengkap",
        "role",
        "is_active",
        "is_staff",
        "created_at",
    )
    search_fields = ("nik", "nama_lengkap", "nomor_hp")
    list_filter = ("role", "is_active", "is_staff")

    fieldsets = (
        (None, {"fields": ("nik", "password")}),
        ("Info Personal", {"fields": ("nama_lengkap", "nomor_hp")}),
        ("Role & Status", {"fields": ("role", "is_active", "is_staff", "is_superuser")}),
        ("Permissions", {"fields": ("groups", "user_permissions")}),
        ("Timestamps", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    readonly_fields = ("created_at", "updated_at", "last_login")

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("nik", "nama_lengkap", "nomor_hp", "role", "password1", "password2"),
            },
        ),
    )