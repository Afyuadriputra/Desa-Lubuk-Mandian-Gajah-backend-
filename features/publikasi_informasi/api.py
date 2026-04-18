# features/publikasi_informasi/api.py
from typing import List, Optional
from ninja import Router

from .schemas import BuatPublikasiIn, PublikasiListOut, PublikasiDetailOut, UbahStatusIn
from .services import PublikasiService
from toolbox.api.auth import AuthAdminOnly

router = Router(tags=["Publikasi Informasi (CMS)"])
publikasi_service = PublikasiService()

@router.get("/publik", auth=None, response=list[PublikasiListOut])
def list_publikasi_publik_api(request, jenis: Optional[str] = None):
    return publikasi_service.get_publikasi_publik(jenis=jenis)

@router.get("/publik/{slug}", auth=None, response=PublikasiDetailOut)
def detail_publikasi_api(request, slug: str):
    return publikasi_service.get_detail_publik(slug)

@router.post("/admin/buat", auth=AuthAdminOnly, response={201: PublikasiDetailOut})
def buat_publikasi_admin_api(request, payload: BuatPublikasiIn):
    publikasi = publikasi_service.buat_publikasi(
        actor=request.user,
        judul=payload.judul,
        konten_html=payload.konten_html,
        jenis=payload.jenis,
        status=payload.status
    )
    return 201, publikasi

@router.put("/admin/{slug}/status", auth=AuthAdminOnly, response=PublikasiDetailOut)
def ubah_status_publikasi_api(request, slug: str, payload: UbahStatusIn):
    updated_publikasi = publikasi_service.ubah_status(
        actor=request.user,
        slug=slug,
        new_status=payload.status
    )
    return updated_publikasi