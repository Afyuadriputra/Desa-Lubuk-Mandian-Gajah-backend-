# features/pengaduan_warga/views.py

import json

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from features.pengaduan_warga.domain import PengaduanError
from features.pengaduan_warga.services import (
    FileUploadError,
    PengaduanNotFoundError,
    PengaduanService,
    PermissionDeniedError,
)
from toolbox.security.auth import is_active_user

pengaduan_service = PengaduanService()


def _parse_json_body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


@require_POST
def buat_pengaduan_view(request):
    """Menerima Multipart/Form-Data karena ada upload gambar opsional."""
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    kategori = request.POST.get("kategori", "")
    judul = request.POST.get("judul", "")
    deskripsi = request.POST.get("deskripsi", "")
    foto_bukti = request.FILES.get("foto_bukti")

    try:
        pengaduan = pengaduan_service.buat_pengaduan(
            actor=actor,
            kategori=kategori,
            judul=judul,
            deskripsi=deskripsi,
            foto_bukti=foto_bukti
        )
    except PengaduanError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except FileUploadError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)

    return JsonResponse(
        {
            "detail": "Pengaduan berhasil dibuat.",
            "data": {
                "id": pengaduan.id,
                "status": pengaduan.status,
                "kategori": pengaduan.kategori,
                "created_at": pengaduan.created_at.isoformat(),
            }
        },
        status=201
    )


@require_GET
def list_pengaduan_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    qs = pengaduan_service.list_pengaduan(actor)
    data = [
        {
            "id": p.id,
            "judul": p.judul,
            "kategori": p.kategori,
            "status": p.status,
            "pelapor": p.pelapor.nama_lengkap,
            "created_at": p.created_at.isoformat(),
        } for p in qs
    ]

    return JsonResponse({"data": data}, status=200)


@require_GET
def detail_pengaduan_view(request, pengaduan_id):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    try:
        pengaduan = pengaduan_service.get_pengaduan_detail(actor, pengaduan_id)
    except PengaduanNotFoundError as exc:
        return JsonResponse({"detail": str(exc)}, status=404)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)

    histori = [
        {
            "status_to": h.status_to,
            "notes": h.notes,
            "created_at": h.created_at.isoformat(),
            "changed_by": h.changed_by.nama_lengkap if h.changed_by else "System"
        }
        for h in pengaduan.histori_tindak_lanjut.all()
    ]

    return JsonResponse(
        {
            "data": {
                "id": pengaduan.id,
                "kategori": pengaduan.kategori,
                "judul": pengaduan.judul,
                "deskripsi": pengaduan.deskripsi,
                "status": pengaduan.status,
                "foto_bukti_url": pengaduan.foto_bukti.url if pengaduan.foto_bukti else None,
                "pelapor": {
                    "nama_lengkap": pengaduan.pelapor.nama_lengkap,
                },
                "histori": histori,
                "created_at": pengaduan.created_at.isoformat(),
                "updated_at": pengaduan.updated_at.isoformat(),
            }
        },
        status=200
    )


@require_POST
def proses_pengaduan_view(request, pengaduan_id):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Payload JSON tidak valid."}, status=400)

    try:
        pengaduan = pengaduan_service.proses_pengaduan(
            actor=actor,
            pengaduan_id=pengaduan_id,
            new_status=payload.get("status", ""),
            notes=payload.get("notes")
        )
    except PengaduanError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)
    except PengaduanNotFoundError as exc:
        return JsonResponse({"detail": str(exc)}, status=404)

    return JsonResponse(
        {
            "detail": "Status pengaduan berhasil diperbarui.",
            "data": {
                "id": pengaduan.id,
                "status": pengaduan.status,
            }
        },
        status=200
    )