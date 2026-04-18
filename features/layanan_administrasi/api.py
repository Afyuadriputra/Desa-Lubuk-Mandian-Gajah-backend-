from ninja import Router
from .schemas import SuratIn, SuratOut, ProsesSuratIn
from .services import SuratService
from toolbox.api.auth import AuthActiveUser, AuthAdminOnly

router = Router(tags=["Layanan Administrasi"])
surat_service = SuratService()

@router.post("/surat/ajukan", auth=AuthActiveUser, response={201: SuratOut})
def ajukan_surat_api(request, payload: SuratIn):
    surat = surat_service.ajukan_surat(
        actor=request.user, 
        **payload.dict(exclude_unset=True)
    )
    return 201, surat

@router.get("/surat", auth=AuthActiveUser, response=list[SuratOut])
def list_surat_api(request):
    return surat_service.list_surat(request.user)

@router.post("/surat/{surat_id}/proses", auth=AuthAdminOnly, response=SuratOut)
def proses_surat_api(request, surat_id: str, payload: ProsesSuratIn):
    # Kita petakan secara manual agar nama parameter di API 
    # sinkron dengan nama parameter di Service Layer Anda.
    surat = surat_service.proses_surat(
        actor=request.user,
        surat_id=surat_id,
        new_status=payload.status,        # Map 'status' ke 'new_status'
        notes=payload.notes,               # Nama sudah sama
        nomor_surat=payload.nomor_surat,
        rejection_reason=payload.rejection_reason
    )
    return surat