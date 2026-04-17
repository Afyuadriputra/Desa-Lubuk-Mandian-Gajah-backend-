# features/publikasi_informasi/views.py

import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from features.publikasi_informasi.services import PublikasiService, PublikasiError, PublikasiAccessError
from toolbox.security.auth import is_active_user

publikasi_service = PublikasiService()

@require_GET
def list_publikasi_publik_view(request):
    jenis = request.GET.get("jenis") # Opsional: ?jenis=BERITA
    qs = publikasi_service.get_publikasi_publik(jenis)
    data = [{
        "judul": p.judul, 
        "slug": p.slug, 
        "jenis": p.jenis,
        "penulis": p.penulis.nama_lengkap if p.penulis else "Admin",
        "published_at": p.published_at.isoformat() if p.published_at else None
    } for p in qs]
    return JsonResponse({"data": data}, status=200)

@require_GET
def detail_publikasi_view(request, slug):
    try:
        p = publikasi_service.get_detail_publik(slug)
        return JsonResponse({
            "data": {
                "judul": p.judul,
                "konten_html": p.konten_html, # Aman, sudah disanitasi saat disave
                "jenis": p.jenis,
                "penulis": p.penulis.nama_lengkap if p.penulis else "Admin",
                "published_at": p.published_at.isoformat() if p.published_at else None
            }
        }, status=200)
    except PublikasiError as e:
        return JsonResponse({"detail": str(e)}, status=404)

@require_POST
def buat_publikasi_admin_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor): 
        return JsonResponse({"detail": "Unauthorized"}, status=401)
        
    data = json.loads(request.body.decode("utf-8") or "{}")
    try:
        publikasi = publikasi_service.buat_publikasi(
            actor=actor,
            judul=data.get("judul"),
            konten_html=data.get("konten_html"),
            jenis=data.get("jenis", "BERITA"),
            status=data.get("status", "DRAFT")
        )
        return JsonResponse({"detail": "Publikasi berhasil dibuat", "slug": publikasi.slug}, status=201)
    except (PublikasiError, PublikasiAccessError) as e:
        return JsonResponse({"detail": str(e)}, status=400)