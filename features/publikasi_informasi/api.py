# features/publikasi_informasi/api.py
from typing import List, Optional
from ninja import Router

from .schemas import (
    BuatPublikasiIn,
    PublikasiDetailOut,
    PublikasiListOut,
    UbahStatusIn,
    UpdatePublikasiIn,
)
from .services import PublikasiService
from toolbox.api.auth import AuthAdminOnly

router = Router(tags=["Publikasi Informasi (CMS)"])
publikasi_service = PublikasiService()


def _serialize(schema_cls, obj):
    return schema_cls.model_validate(obj, from_attributes=True).model_dump(mode="json")


def _serialize_public_detail(obj):
    data = _serialize(PublikasiDetailOut, obj)
    data.pop("status", None)
    return data


@router.get("/publik", auth=None, response=list[PublikasiListOut])
def list_publikasi_publik_api(request, jenis: Optional[str] = None):
    return publikasi_service.get_publikasi_publik(jenis=jenis)

@router.get("/publik/{slug}", auth=None, response=PublikasiDetailOut)
def detail_publikasi_api(request, slug: str):
    return publikasi_service.get_detail_publik(slug)


@router.get("/admin", auth=AuthAdminOnly, response=list[PublikasiDetailOut], url_name="publikasi-admin-list")
def list_publikasi_admin_api(request):
    return publikasi_service.list_publikasi_admin(request.user)

@router.post("/admin/buat", auth=AuthAdminOnly, response={201: PublikasiDetailOut}, url_name="publikasi-admin-buat")
def buat_publikasi_admin_api(request, payload: BuatPublikasiIn):
    publikasi = publikasi_service.buat_publikasi(
        actor=request.user,
        judul=payload.judul,
        konten_html=payload.konten_html,
        jenis=payload.jenis,
        status=payload.status
    )
    return 201, publikasi

@router.put(
    "/admin/{slug}/status",
    auth=AuthAdminOnly,
    response=PublikasiDetailOut,
    url_name="publikasi-admin-ubah-status",
)
def ubah_status_publikasi_api(request, slug: str, payload: UbahStatusIn):
    updated_publikasi = publikasi_service.ubah_status(
        actor=request.user,
        slug=slug,
        new_status=payload.status
    )
    return updated_publikasi


@router.put("/admin/{slug}", auth=AuthAdminOnly, response=PublikasiDetailOut, url_name="publikasi-admin-update")
def update_publikasi_admin_api(request, slug: str, payload: UpdatePublikasiIn):
    return publikasi_service.ubah_publikasi(
        actor=request.user,
        slug=slug,
        judul=payload.judul,
        konten_html=payload.konten_html,
        jenis=payload.jenis,
        status=payload.status,
    )


@router.delete("/admin/{slug}", auth=AuthAdminOnly, response=dict, url_name="publikasi-admin-delete")
def delete_publikasi_admin_api(request, slug: str):
    publikasi_service.hapus_publikasi(actor=request.user, slug=slug)
    return {"detail": "Publikasi berhasil dihapus."}


@router.get("/mvp/publik", auth=None, response=dict, url_name="publikasi-publik-list")
def list_publikasi_publik_mvp_api(request, jenis: Optional[str] = None):
    publikasi = publikasi_service.get_publikasi_publik(jenis=jenis)
    return {"data": [_serialize(PublikasiListOut, item) for item in publikasi]}


@router.get("/mvp/publik/{slug}", auth=None, response=dict, url_name="publikasi-detail")
def detail_publikasi_mvp_api(request, slug: str):
    publikasi = publikasi_service.get_detail_publik(slug)
    return {"data": _serialize_public_detail(publikasi)}
