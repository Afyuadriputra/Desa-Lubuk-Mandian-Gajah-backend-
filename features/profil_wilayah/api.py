from ninja import Router, Form, File
from ninja.files import UploadedFile

from .schemas import (
    TambahDusunIn,
    UpdateDusunIn,
    TambahPerangkatIn,
    UpdatePerangkatIn,
    UpdateProfilDesaIn,
    DusunOut,
    ProfilPublikAggregatedOut,
    ProfilDesaOut,
    PerangkatAdminOut,
)
from .services import DusunService, PerangkatService, ProfilDesaService
from toolbox.api.auth import AuthAdminOnly

router = Router(tags=["Profil Wilayah"])

dusun_service = DusunService()
perangkat_service = PerangkatService()
profil_service = ProfilDesaService()


@router.get("/publik", response=ProfilPublikAggregatedOut)
def profil_publik_api(request):
    profil = profil_service.get_profil()
    perangkat = perangkat_service.get_perangkat_publik()
    return {
        "profil": profil,
        "perangkat": list(perangkat),
    }


@router.get("/admin/dusun", auth=AuthAdminOnly, response=list[DusunOut])
def list_dusun_api(request):
    return list(dusun_service.get_semua_dusun())


@router.post("/admin/dusun", auth=AuthAdminOnly, response={201: DusunOut})
def tambah_dusun_api(request, payload: TambahDusunIn):
    dusun = dusun_service.tambah_dusun(
        actor=request.user,
        nama_dusun=payload.nama_dusun,
        kepala_dusun=payload.kepala_dusun,
    )
    return 201, dusun


@router.put("/admin/dusun/{dusun_id}", auth=AuthAdminOnly, response=DusunOut)
def ubah_dusun_api(request, dusun_id: int, payload: UpdateDusunIn):
    return dusun_service.ubah_dusun(
        actor=request.user,
        dusun_id=dusun_id,
        nama_dusun=payload.nama_dusun,
        kepala_dusun=payload.kepala_dusun,
    )


@router.delete("/admin/dusun/{dusun_id}", auth=AuthAdminOnly, response=dict)
def hapus_dusun_api(request, dusun_id: int):
    dusun_service.hapus_dusun(actor=request.user, dusun_id=dusun_id)
    return {"detail": "Dusun berhasil dihapus"}


@router.get("/admin/perangkat", auth=AuthAdminOnly, response=list[PerangkatAdminOut])
def list_perangkat_admin_api(request):
    return list(perangkat_service.get_semua_perangkat())


@router.post("/admin/perangkat", auth=AuthAdminOnly, response={201: dict})
def tambah_perangkat_api(
    request,
    payload: Form[TambahPerangkatIn],
    foto: File[UploadedFile] = None,
):
    perangkat = perangkat_service.tambah_perangkat(
        actor=request.user,
        user_id=payload.user_id,
        jabatan=payload.jabatan,
        is_published=payload.is_published,
        foto=foto,
    )
    return 201, {"detail": "Perangkat berhasil ditambahkan", "id": perangkat.id}


@router.put("/admin/perangkat/{perangkat_id}", auth=AuthAdminOnly, response=dict)
def ubah_perangkat_api(request, perangkat_id: int, payload: UpdatePerangkatIn):
    perangkat = perangkat_service.ubah_perangkat(
        actor=request.user,
        perangkat_id=perangkat_id,
        user_id=payload.user_id,
        jabatan=payload.jabatan,
        is_published=payload.is_published,
        foto=None,
    )
    return {"detail": "Perangkat berhasil diperbarui", "id": perangkat.id}


@router.delete("/admin/perangkat/{perangkat_id}", auth=AuthAdminOnly, response=dict)
def hapus_perangkat_api(request, perangkat_id: int):
    perangkat_service.hapus_perangkat(actor=request.user, perangkat_id=perangkat_id)
    return {"detail": "Perangkat berhasil dihapus"}


@router.put("/admin/profil", auth=AuthAdminOnly, response=ProfilDesaOut)
def update_profil_desa_api(request, payload: UpdateProfilDesaIn):
    return profil_service.perbarui_profil(
        actor=request.user,
        visi=payload.visi,
        misi=payload.misi,
        sejarah=payload.sejarah,
    )