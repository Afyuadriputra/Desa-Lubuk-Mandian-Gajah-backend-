from ninja import Router
from .schemas import ProsesSuratIn, SuratDetailOut, SuratIn, SuratOut
from .services import SuratService
from toolbox.api.auth import AuthActiveUser, AuthAdminOnly

router = Router(tags=["Layanan Administrasi"])
surat_service = SuratService()

def _serialize(schema_cls, obj):
    return schema_cls.model_validate(obj, from_attributes=True).model_dump(mode="json")


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


@router.get("/surat/{surat_id}", auth=AuthActiveUser, response=SuratDetailOut)
def detail_surat_api(request, surat_id: str):
    return surat_service.get_surat_detail(request.user, surat_id)

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


@router.get("/surat/{surat_id}/download", auth=AuthActiveUser)
def download_pdf_surat_api(request, surat_id: str):
    return surat_service.download_pdf(request.user, surat_id)


@router.post("/mvp/surat/ajukan", auth=AuthActiveUser, response={201: dict}, url_name="surat-ajukan")
def ajukan_surat_mvp_api(request, payload: SuratIn):
    surat = surat_service.ajukan_surat(
        actor=request.user,
        **payload.dict(exclude_unset=True),
    )
    return 201, {"data": _serialize(SuratOut, surat)}


@router.get("/mvp/surat", auth=AuthActiveUser, response=dict, url_name="surat-list")
def list_surat_mvp_api(request):
    surat_list = surat_service.list_surat(request.user)
    return {"data": [_serialize(SuratOut, surat) for surat in surat_list]}


@router.get("/mvp/surat/{surat_id}", auth=AuthActiveUser, response=dict, url_name="surat-detail")
def detail_surat_mvp_api(request, surat_id: str):
    surat = surat_service.get_surat_detail(request.user, surat_id)
    return {"data": _serialize(SuratDetailOut, surat)}


@router.post(
    "/mvp/surat/{surat_id}/proses",
    auth=AuthAdminOnly,
    response=dict,
    url_name="surat-proses",
)
def proses_surat_mvp_api(request, surat_id: str, payload: ProsesSuratIn):
    surat = surat_service.proses_surat(
        actor=request.user,
        surat_id=surat_id,
        new_status=payload.status,
        notes=payload.notes,
        nomor_surat=payload.nomor_surat,
        rejection_reason=payload.rejection_reason,
    )
    return {"data": _serialize(SuratOut, surat)}


@router.get(
    "/mvp/surat/{surat_id}/download",
    auth=AuthActiveUser,
    url_name="surat-download-pdf",
)
def download_pdf_surat_mvp_api(request, surat_id: str):
    return surat_service.download_pdf(request.user, surat_id)
