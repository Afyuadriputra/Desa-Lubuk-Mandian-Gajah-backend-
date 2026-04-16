# features/layanan_administrasi/views.py

import json

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from features.layanan_administrasi.domain import LayananSuratError
from features.layanan_administrasi.services import (
    LayananSuratNotFoundError,
    PermissionDeniedError,
    SuratService,
)
from toolbox.security.auth import is_active_user

surat_service = SuratService()


def _parse_json_body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


@require_POST
def ajukan_surat_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Payload JSON tidak valid."}, status=400)

    try:
        surat = surat_service.ajukan_surat(
            actor=actor,
            jenis_surat=payload.get("jenis_surat", ""),
            keperluan=payload.get("keperluan", "")
        )
    except LayananSuratError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)

    return JsonResponse(
        {
            "detail": "Pengajuan surat berhasil.",
            "data": {
                "id": str(surat.id),
                "jenis_surat": surat.jenis_surat,
                "status": surat.status,
                "created_at": surat.created_at.isoformat(),
            }
        },
        status=201
    )


@require_GET
def list_surat_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    qs = surat_service.list_surat(actor)
    data = [
        {
            "id": str(s.id),
            "jenis_surat": s.jenis_surat,
            "status": s.status,
            "pemohon": s.pemohon.nama_lengkap,
            "created_at": s.created_at.isoformat(),
        } for s in qs
    ]

    return JsonResponse({"data": data}, status=200)


@require_GET
def detail_surat_view(request, surat_id):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    try:
        surat = surat_service.get_surat_detail(actor, surat_id)
    except LayananSuratNotFoundError as exc:
        return JsonResponse({"detail": str(exc)}, status=404)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)

    return JsonResponse(
        {
            "data": {
                "id": str(surat.id),
                "jenis_surat": surat.jenis_surat,
                "keperluan": surat.keperluan,
                "status": surat.status,
                "nomor_surat": surat.nomor_surat,
                "rejection_reason": surat.rejection_reason,
                "pdf_url": surat.pdf_file.url if surat.pdf_file else None,
                "pemohon": {
                    "id": str(surat.pemohon.id),
                    "nama_lengkap": surat.pemohon.nama_lengkap,
                    "nik": surat.pemohon.nik,
                },
                "created_at": surat.created_at.isoformat(),
                "updated_at": surat.updated_at.isoformat(),
            }
        },
        status=200
    )


@require_POST
def proses_surat_view(request, surat_id):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Payload JSON tidak valid."}, status=400)

    try:
        surat = surat_service.proses_surat(
            actor=actor,
            surat_id=surat_id,
            new_status=payload.get("status", ""),
            notes=payload.get("notes"),
            nomor_surat=payload.get("nomor_surat"),
            rejection_reason=payload.get("rejection_reason")
        )
    except LayananSuratError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)
    except LayananSuratNotFoundError as exc:
        return JsonResponse({"detail": str(exc)}, status=404)

    return JsonResponse(
        {
            "detail": "Status surat berhasil diperbarui.",
            "data": {
                "id": str(surat.id),
                "status": surat.status,
            }
        },
        status=200
    )