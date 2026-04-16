# features/potensi_ekonomi/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from features.potensi_ekonomi.domain import PotensiEkonomiError
from features.potensi_ekonomi.services import (
    FileUploadError,
    PermissionDeniedError,
    PotensiEkonomiService,
    UnitUsahaNotFoundError,
)
from toolbox.security.auth import is_active_user

ekonomi_service = PotensiEkonomiService()


@require_GET
def katalog_publik_view(request):
    """Endpoint untuk warga melihat katalog BUMDes/Wisata yang aktif."""
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    try:
        qs = ekonomi_service.get_katalog_publik(actor)
        data = [
            {
                "id": u.id,
                "nama_usaha": u.nama_usaha,
                "kategori": u.kategori,
                "deskripsi": u.deskripsi,
                "harga_tiket": u.harga_tiket,
                "foto_url": u.foto_utama.url if u.foto_utama else None,
            } for u in qs
        ]
        return JsonResponse({"data": data}, status=200)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)


@require_GET
def list_admin_view(request):
    """Endpoint untuk admin melihat semua data (termasuk draft)."""
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    try:
        qs = ekonomi_service.get_semua_unit_admin(actor)
        data = [
            {
                "id": u.id,
                "nama_usaha": u.nama_usaha,
                "kategori": u.kategori,
                "is_published": u.is_published,
                "created_at": u.created_at.isoformat(),
            } for u in qs
        ]
        return JsonResponse({"data": data}, status=200)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)


@require_POST
def buat_unit_usaha_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    # Menangani form-data karena ada upload gambar
    data_payload = {
        "nama_usaha": request.POST.get("nama_usaha"),
        "kategori": request.POST.get("kategori"),
        "deskripsi": request.POST.get("deskripsi"),
        "fasilitas": request.POST.get("fasilitas"),
        "kontak_wa": request.POST.get("kontak_wa"),
        "harga_tiket": request.POST.get("harga_tiket"),
        "is_published": request.POST.get("is_published", "false"),
    }
    foto = request.FILES.get("foto_utama")

    try:
        unit = ekonomi_service.buat_unit_usaha(actor, data_payload, foto)
    except PotensiEkonomiError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except FileUploadError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)

    return JsonResponse(
        {
            "detail": "Data BUMDes/Wisata berhasil ditambahkan.",
            "data": {
                "id": unit.id,
                "nama_usaha": unit.nama_usaha,
                "is_published": unit.is_published,
            }
        },
        status=201
    )


@require_GET
def detail_unit_view(request, unit_id):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    try:
        unit = ekonomi_service.get_detail_unit(actor, unit_id)
    except UnitUsahaNotFoundError as exc:
        return JsonResponse({"detail": str(exc)}, status=404)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)

    return JsonResponse(
        {
            "data": {
                "id": unit.id,
                "nama_usaha": unit.nama_usaha,
                "kategori": unit.kategori,
                "deskripsi": unit.deskripsi,
                "fasilitas": unit.fasilitas,
                "kontak_wa": unit.kontak_wa,
                "harga_tiket": unit.harga_tiket,
                "is_published": unit.is_published,
                "foto_url": unit.foto_utama.url if unit.foto_utama else None,
            }
        },
        status=200
    )