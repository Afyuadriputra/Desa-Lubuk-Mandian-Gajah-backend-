# features/pengaduan_warga/api.py

from typing import List
from ninja import Router, Form, File
from ninja.files import UploadedFile

from .schemas import (
    BuatPengaduanIn, 
    PengaduanListOut, 
    PengaduanDetailOut, 
    ProsesPengaduanIn
)
from .services import PengaduanService
from toolbox.api.auth import AuthActiveUser, AuthAdminOnly

router = Router(tags=["Pengaduan Warga"])

# Dependency Inversion Principle: Kita inject class service
pengaduan_service = PengaduanService()


@router.post("/buat", auth=AuthActiveUser, response={201: PengaduanListOut})
def buat_pengaduan_api(
    request, 
    payload: Form[BuatPengaduanIn], 
    foto_bukti: File[UploadedFile] = None
):
    """
    Endpoint untuk warga membuat pengaduan.
    Menerima Multipart/Form-Data karena ada upload foto opsional.
    """
    pengaduan = pengaduan_service.buat_pengaduan(
        actor=request.user,
        kategori=payload.kategori,
        judul=payload.judul,
        deskripsi=payload.deskripsi,
        foto_bukti=foto_bukti
    )
    return 201, pengaduan


@router.get("/", auth=AuthActiveUser, response=List[PengaduanListOut])
def list_pengaduan_api(request):
    """Menampilkan daftar pengaduan (Warga lihat miliknya, Admin lihat semua)."""
    return pengaduan_service.list_pengaduan(request.user)


@router.get("/{pengaduan_id}", auth=AuthActiveUser, response=PengaduanDetailOut)
def detail_pengaduan_api(request, pengaduan_id: int):
    """Menampilkan detail pengaduan beserta riwayat tindak lanjutnya."""
    return pengaduan_service.get_pengaduan_detail(request.user, pengaduan_id)


@router.post("/{pengaduan_id}/proses", auth=AuthAdminOnly, response=PengaduanListOut)
def proses_pengaduan_api(request, pengaduan_id: int, payload: ProsesPengaduanIn):
    """
    Endpoint untuk Admin memproses/mengubah status pengaduan.
    Hanya menerima JSON.
    """
    updated_pengaduan = pengaduan_service.proses_pengaduan(
        actor=request.user,
        pengaduan_id=pengaduan_id,
        new_status=payload.status,
        notes=payload.notes
    )
    return updated_pengaduan