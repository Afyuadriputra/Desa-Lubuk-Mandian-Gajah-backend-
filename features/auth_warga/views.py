# features/auth_warga/views.py

import json

from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from features.auth_warga.domain import (
    AuthenticationFailedError,
    DuplicateNIKError,
    InactiveAccountError,
    InvalidNIKError,
    InvalidRoleError,
)
from features.auth_warga.services import (
    AuthService,
    PermissionDeniedError,
    UserNotFoundError,
)
from toolbox.security.auth import is_active_user

auth_service = AuthService()


def _parse_json_body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


@require_POST
def login_view(request):
    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Payload JSON tidak valid."}, status=400)

    nik = payload.get("nik", "")
    password = payload.get("password", "")

    if not nik or not password:
        return JsonResponse({"detail": "NIK dan kata sandi wajib diisi."}, status=400)

    try:
        result = auth_service.login_user(
            request=request,
            nik=nik,
            password=password,
        )
    except InvalidNIKError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except InactiveAccountError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)
    except AuthenticationFailedError as exc:
        return JsonResponse({"detail": str(exc)}, status=401)

    login(request, result.user)
    return JsonResponse(
        {
            "detail": result.message,
            "data": {
                "id": str(result.user.id),
                "nik": result.user.nik,
                "nama_lengkap": result.user.nama_lengkap,
                "role": result.user.role,
                "is_active": result.user.is_active,
            },
        },
        status=200,
    )


@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({"detail": "Logout berhasil."}, status=200)


@require_GET
def me_view(request):
    user = getattr(request, "user", None)
    if not is_active_user(user):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    return JsonResponse(
        {
            "data": {
                "id": str(user.id),
                "nik": user.nik,
                "nama_lengkap": user.nama_lengkap,
                "nomor_hp": user.nomor_hp,
                "role": user.role,
                "is_active": user.is_active,
            }
        },
        status=200,
    )


@require_POST
def create_warga_user_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Payload JSON tidak valid."}, status=400)

    try:
        user = auth_service.create_warga_account(
            actor=actor,
            nik=payload.get("nik", ""),
            password=payload.get("password", ""),
            nama_lengkap=payload.get("nama_lengkap", ""),
            nomor_hp=payload.get("nomor_hp"),
            is_active=payload.get("is_active", True),
        )
    except (InvalidNIKError, DuplicateNIKError, InvalidRoleError) as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)
    except ValueError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)

    return JsonResponse(
        {
            "detail": "Akun warga berhasil dibuat.",
            "data": {
                "id": str(user.id),
                "nik": user.nik,
                "nama_lengkap": user.nama_lengkap,
                "role": user.role,
                "is_active": user.is_active,
            },
        },
        status=201,
    )


@require_POST
def create_admin_user_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Payload JSON tidak valid."}, status=400)

    try:
        user = auth_service.create_admin_account(
            actor=actor,
            nik=payload.get("nik", ""),
            password=payload.get("password", ""),
            nama_lengkap=payload.get("nama_lengkap", ""),
            role=payload.get("role", ""),
            nomor_hp=payload.get("nomor_hp"),
            is_active=payload.get("is_active", True),
        )
    except (InvalidNIKError, DuplicateNIKError, InvalidRoleError) as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)
    except ValueError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)

    return JsonResponse(
        {
            "detail": "Akun admin berhasil dibuat.",
            "data": {
                "id": str(user.id),
                "nik": user.nik,
                "nama_lengkap": user.nama_lengkap,
                "role": user.role,
                "is_active": user.is_active,
            },
        },
        status=201,
    )


@require_POST
def activate_user_view(request, user_id):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    try:
        target_user = auth_service.activate_account(actor=actor, target_user_id=user_id)
    except UserNotFoundError as exc:
        return JsonResponse({"detail": str(exc)}, status=404)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)

    return JsonResponse(
        {
            "detail": "Akun berhasil diaktifkan.",
            "data": {
                "id": str(target_user.id),
                "nik": target_user.nik,
                "nama_lengkap": target_user.nama_lengkap,
                "role": target_user.role,
                "is_active": target_user.is_active,
            },
        },
        status=200,
    )


@require_POST
def deactivate_user_view(request, user_id):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    try:
        target_user = auth_service.deactivate_account(actor=actor, target_user_id=user_id)
    except UserNotFoundError as exc:
        return JsonResponse({"detail": str(exc)}, status=404)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)

    return JsonResponse(
        {
            "detail": "Akun berhasil dinonaktifkan.",
            "data": {
                "id": str(target_user.id),
                "nik": target_user.nik,
                "nama_lengkap": target_user.nama_lengkap,
                "role": target_user.role,
                "is_active": target_user.is_active,
            },
        },
        status=200,
    )