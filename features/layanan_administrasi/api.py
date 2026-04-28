# features/layanan_administrasi/api.py

"""
Layer: API

Tanggung jawab:
- Menerima request HTTP.
- Mapping input ke service.
- Return response.
- Tidak berisi business logic.
"""

from ninja import File, Form, Router
from ninja.files import UploadedFile

from .schemas import (
    ProsesSuratIn,
    SuratDetailOut,
    SuratIn,
    SuratOut,
    TemplateSuratCreateIn,
    TemplateSuratOut,
)
from .services import SuratService, TemplateSuratService
from toolbox.api.auth import AuthActiveUser, AuthAdminOnly


router = Router(tags=["Layanan Administrasi"])

surat_service = SuratService()
template_service = TemplateSuratService()


def _serialize(schema_cls, obj):
    return schema_cls.model_validate(obj, from_attributes=True).model_dump(mode="json")


# ============================================================
# Template Surat
# ============================================================

@router.post(
    "/template-surat",
    auth=AuthAdminOnly,
    response={201: TemplateSuratOut},
    url_name="template-surat-create",
)
def upload_template_surat_api(
    request,
    payload: Form[TemplateSuratCreateIn],
    file_template: UploadedFile = File(...),
):
    template = template_service.create_template(
        actor=request.user,
        kode=payload.kode,
        nama=payload.nama,
        deskripsi=payload.deskripsi,
        file_template=file_template,
        is_active=payload.is_active,
    )
    return 201, template


@router.get(
    "/template-surat/aktif",
    auth=AuthActiveUser,
    response=list[TemplateSuratOut],
    url_name="template-surat-active-list",
)
def list_template_surat_aktif_api(request):
    return template_service.list_active_templates()


@router.get(
    "/template-surat",
    auth=AuthAdminOnly,
    response=list[TemplateSuratOut],
    url_name="template-surat-admin-list",
)
def list_template_surat_admin_api(request):
    return template_service.list_all_templates(request.user)


# ============================================================
# Surat
# ============================================================

@router.post("/surat/ajukan", auth=AuthActiveUser, response={201: SuratOut})
def ajukan_surat_api(request, payload: SuratIn):
    surat = surat_service.ajukan_surat(
        actor=request.user,
        template_id=payload.template_id,
        jenis_surat=payload.jenis_surat,
        keperluan=payload.keperluan,
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
    surat = surat_service.proses_surat(
        actor=request.user,
        surat_id=surat_id,
        new_status=payload.status,
        notes=payload.notes,
        nomor_surat=payload.nomor_surat,
        rejection_reason=payload.rejection_reason,
    )
    return surat


@router.get("/surat/{surat_id}/download", auth=AuthActiveUser)
def download_hasil_surat_api(request, surat_id: str):
    return surat_service.download_hasil_surat(request.user, surat_id)


# ============================================================
# MVP Surat
# ============================================================

@router.post("/mvp/surat/ajukan", auth=AuthActiveUser, response={201: dict}, url_name="surat-ajukan")
def ajukan_surat_mvp_api(request, payload: SuratIn):
    surat = surat_service.ajukan_surat(
        actor=request.user,
        template_id=payload.template_id,
        jenis_surat=payload.jenis_surat,
        keperluan=payload.keperluan,
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
    url_name="surat-download",
)
def download_hasil_surat_mvp_api(request, surat_id: str):
    return surat_service.download_hasil_surat(request.user, surat_id)