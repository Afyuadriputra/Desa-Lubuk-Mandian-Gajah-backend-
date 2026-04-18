# features/potensi_ekonomi/api.py

from typing import List
from ninja import Router, Form, File
from ninja.files import UploadedFile

from .schemas import (
    BuatUnitUsahaIn,
    KatalogAdminOut,
    KatalogPublikOut,
    UnitUsahaDetailOut,
    UpdateUnitUsahaIn,
)
from .services import PotensiEkonomiService
from toolbox.api.auth import AuthActiveUser, AuthBumdesManager

router = Router(tags=["Potensi Ekonomi (BUMDes & Wisata)"])

# Dependency Inversion Principle
ekonomi_service = PotensiEkonomiService()


def _serialize(schema_cls, obj):
    return schema_cls.model_validate(obj, from_attributes=True).model_dump(mode="json")


@router.get("/katalog", auth=None, response=List[KatalogPublikOut])
def katalog_publik_api(request):
    """Endpoint untuk warga melihat etalase aktif."""
    return ekonomi_service.get_katalog_publik()


@router.get("/admin/list", auth=AuthActiveUser, response=List[KatalogAdminOut])
def list_admin_api(request):
    """
    Endpoint untuk Admin melihat semua data (termasuk Draft).
    Izin spesifik (can_manage_bumdes) sudah dijaga oleh Service Layer.
    """
    return ekonomi_service.get_semua_unit_admin(request.user)


@router.get("/{unit_id}", auth=None, response=UnitUsahaDetailOut)
def detail_unit_api(request, unit_id: int):
    """Detail spesifik BUMDes/Wisata."""
    actor = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
    return ekonomi_service.get_detail_unit(actor, unit_id)


@router.post("/admin/buat", auth=AuthActiveUser, response={201: KatalogAdminOut})
def buat_unit_usaha_api(
    request, 
    payload: Form[BuatUnitUsahaIn], 
    foto_utama: File[UploadedFile] = None
):
    """
    Endpoint untuk membuat Unit Usaha baru.
    Menerima Multipart/Form-Data karena ada gambar.
    Input HTML dari payload.deskripsi sudah otomatis bersih dari XSS oleh Schema.
    """
    unit = ekonomi_service.buat_unit_usaha(
        actor=request.user,
        data=payload.dict(), # Langsung diubah menjadi dictionary untuk service
        foto=foto_utama
    )
    return 201, unit


@router.put("/admin/{unit_id}", auth=AuthActiveUser, response=UnitUsahaDetailOut)
def ubah_unit_usaha_api(request, unit_id: int, payload: UpdateUnitUsahaIn):
    return ekonomi_service.ubah_unit_usaha(
        actor=request.user,
        unit_id=unit_id,
        data=payload.dict(),
    )


@router.delete("/admin/{unit_id}", auth=AuthActiveUser, response=dict)
def hapus_unit_usaha_api(request, unit_id: int):
    ekonomi_service.hapus_unit_usaha(actor=request.user, unit_id=unit_id)
    return {"detail": "Unit usaha berhasil dihapus."}


@router.get("/mvp/katalog", auth=None, response=dict, url_name="ekonomi-katalog")
def katalog_publik_mvp_api(request):
    katalog = ekonomi_service.get_katalog_publik()
    return {"data": [_serialize(KatalogPublikOut, item) for item in katalog]}


@router.get("/mvp/{unit_id}", auth=None, response=dict, url_name="ekonomi-detail")
def detail_unit_mvp_api(request, unit_id: int):
    actor = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
    unit = ekonomi_service.get_detail_unit(actor, unit_id)
    return {"data": _serialize(UnitUsahaDetailOut, unit)}


@router.get("/mvp/admin/list", auth=AuthBumdesManager, response=dict, url_name="ekonomi-admin-list")
def list_admin_mvp_api(request):
    units = ekonomi_service.get_semua_unit_admin(request.user)
    return {"data": [_serialize(KatalogAdminOut, item) for item in units]}


@router.post("/mvp/admin/buat", auth=AuthBumdesManager, response={201: dict}, url_name="ekonomi-admin-buat")
def buat_unit_usaha_mvp_api(
    request,
    payload: Form[BuatUnitUsahaIn],
    foto_utama: File[UploadedFile] = None,
):
    unit = ekonomi_service.buat_unit_usaha(
        actor=request.user,
        data=payload.dict(),
        foto=foto_utama,
    )
    return 201, {"data": _serialize(UnitUsahaDetailOut, unit)}


@router.put("/mvp/admin/{unit_id}", auth=AuthBumdesManager, response=dict, url_name="ekonomi-admin-update")
def ubah_unit_usaha_mvp_api(request, unit_id: int, payload: UpdateUnitUsahaIn):
    unit = ekonomi_service.ubah_unit_usaha(
        actor=request.user,
        unit_id=unit_id,
        data=payload.dict(),
    )
    return {"data": _serialize(UnitUsahaDetailOut, unit)}


@router.delete("/mvp/admin/{unit_id}", auth=AuthBumdesManager, response=dict, url_name="ekonomi-admin-delete")
def hapus_unit_usaha_mvp_api(request, unit_id: int):
    ekonomi_service.hapus_unit_usaha(actor=request.user, unit_id=unit_id)
    return {"detail": "Unit usaha berhasil dihapus."}
