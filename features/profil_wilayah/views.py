# features/profil_wilayah/views.py

import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from features.profil_wilayah.services import DusunService, PerangkatService, ProfilDesaService
from toolbox.security.auth import is_active_user

dusun_service = DusunService()
perangkat_service = PerangkatService()
profil_service = ProfilDesaService()

@require_GET
def profil_publik_view(request):
    """Menampilkan Visi, Misi, Sejarah dan Perangkat Desa yang aktif."""
    profil = profil_service.get_profil()
    perangkat = perangkat_service.get_perangkat_publik()
    
    return JsonResponse({
        "profil": {"visi": profil.visi, "misi": profil.misi, "sejarah": profil.sejarah},
        "perangkat": [{"jabatan": p.jabatan, "nama": p.user.nama_lengkap, "foto_url": p.foto.url if p.foto else None} for p in perangkat]
    }, status=200)

@require_POST
def tambah_dusun_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor): return JsonResponse({"detail": "Unauthorized"}, status=401)
    
    data = json.loads(request.body.decode("utf-8") or "{}")
    try:
        dusun = dusun_service.tambah_dusun(actor, data.get("nama_dusun"), data.get("kepala_dusun"))
        return JsonResponse({"detail": "Dusun berhasil ditambahkan", "id": dusun.id}, status=201)
    except Exception as e:
        return JsonResponse({"detail": str(e)}, status=400)

@require_POST
def tambah_perangkat_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor): return JsonResponse({"detail": "Unauthorized"}, status=401)
    
    try:
        perangkat = perangkat_service.tambah_perangkat(
            actor=actor,
            user_id=request.POST.get("user_id"),
            jabatan=request.POST.get("jabatan"),
            is_published=request.POST.get("is_published", "false").lower() == "true",
            foto=request.FILES.get("foto")
        )
        return JsonResponse({"detail": "Perangkat berhasil ditambahkan", "id": perangkat.id}, status=201)
    except Exception as e:
        return JsonResponse({"detail": str(e)}, status=400)