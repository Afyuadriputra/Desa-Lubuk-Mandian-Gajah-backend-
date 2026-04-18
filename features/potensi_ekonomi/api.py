# features/potensi_ekonomi/api.py

from typing import List
from ninja import Router, Form, File
from ninja.files import UploadedFile

from .schemas import (
    BuatUnitUsahaIn, 
    KatalogPublikOut, 
    KatalogAdminOut, 
    UnitUsahaDetailOut
)
from .services import PotensiEkonomiService
from toolbox.api.auth import AuthActiveUser

router = Router(tags=["Potensi Ekonomi (BUMDes & Wisata)"])

# Dependency Inversion Principle
ekonomi_service = PotensiEkonomiService()


@router.get("/katalog", auth=AuthActiveUser, response=List[KatalogPublikOut])
def katalog_publik_api(request):
    """Endpoint untuk warga melihat etalase aktif."""
    return ekonomi_service.get_katalog_publik(request.user)


@router.get("/admin/list", auth=AuthActiveUser, response=List[KatalogAdminOut])
def list_admin_api(request):
    """
    Endpoint untuk Admin melihat semua data (termasuk Draft).
    Izin spesifik (can_manage_bumdes) sudah dijaga oleh Service Layer.
    """
    return ekonomi_service.get_semua_unit_admin(request.user)


@router.get("/{unit_id}", auth=AuthActiveUser, response=UnitUsahaDetailOut)
def detail_unit_api(request, unit_id: int):
    """Detail spesifik BUMDes/Wisata."""
    return ekonomi_service.get_detail_unit(request.user, unit_id)


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